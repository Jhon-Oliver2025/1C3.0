require('dotenv').config();

// Remover as linhas 18-19 e 228-229
const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const app = express();
const PORT = process.env.PORT || 5002;

// Configuração JWT
const JWT_SECRET = process.env.JWT_SECRET || 'fallback-secret-key';

const USERS_FILE = path.join(__dirname, 'users.json');

// NEW: Environment variables for Evo AI agent
const EVO_AI_AGENT_BASE_URL = process.env.EVO_AI_AGENT_BASE_URL;
const EVO_AI_API_KEY = process.env.EVO_AI_API_KEY;

// Configuração CORS mais específica
app.use(cors({
    origin: 'http://localhost:5173', // Permitir a origem do frontend Vite
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());

// Função para carregar usuários do arquivo JSON
async function loadUsers() {
    try {
        const data = await fs.readFile(USERS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            // Arquivo não existe, retorna um array vazio
            return [];
        }
        console.error('Erro ao carregar usuários:', error);
        return []; // Em caso de erro, retorna array vazio para evitar quebrar a aplicação
    }
}

// Função para salvar usuários no arquivo JSON
async function saveUsers(users) {
    try {
        await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2), 'utf8');
    } catch (error) {
        console.error('Erro ao salvar usuários:', error);
    }
}

// Middlewares
// app.use(cors()); // REMOVIDO: Duplicado e pode anular a configuração específica acima
app.use(express.json());

// Rota de teste simples
app.get('/', (req, res) => {
    res.send('Backend está funcionando!');
});

// Rota de Registro de Usuário
app.post('/api/register', async (req, res) => {
    const { email, password } = req.body; // Alterado de 'username' para 'email'

    if (!email || !password) {
        return res.status(400).json({ message: 'Email e senha são obrigatórios.' }); // Mensagem ajustada
    }

    try {
        const users = await loadUsers();

        // Verifica se o usuário já existe pelo email
        if (users.find(user => user.email === email)) { // Alterado para verificar 'email'
            return res.status(409).json({ message: 'Email já registrado.' }); // Mensagem ajustada
        }

        // Gera o hash da senha
        const hashedPassword = await bcrypt.hash(password, 10); // 10 é o saltRounds

        // Cria o novo usuário
        const newUser = {
            id: users.length > 0 ? Math.max(...users.map(u => u.id)) + 1 : 1, // Gera um ID simples
            email, // Alterado de 'username' para 'email'
            password: hashedPassword,
            isAdmin: false // Define como não-admin por padrão
        };

        users.push(newUser);
        await saveUsers(users);

        res.status(201).json({ message: 'Usuário registrado com sucesso!' });

    } catch (error) {
        console.error('Erro no registro:', error);
        res.status(500).json({ message: 'Erro interno do servidor.' });
    }
});

// Rota de Login modificada
app.post('/api/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ message: 'Email e senha são obrigatórios.' });
    }

    try {
        const users = await loadUsers();
        const user = users.find(u => u.email === email);

        if (!user || !(await bcrypt.compare(password, user.password))) {
            return res.status(401).json({ message: 'Credenciais inválidas.' });
        }

        // Gera o token com informações adicionais
        const token = jwt.sign(
            {
                id: user.id,
                email: user.email,
                isAdmin: user.isAdmin,
                iat: Math.floor(Date.now() / 1000)
            },
            JWT_SECRET,
            { expiresIn: '1h' }
        );

        // Resposta com mais informações
        res.status(200).json({
            message: 'Login bem-sucedido!',
            token,
            user: {
                id: user.id,
                email: user.email,
                isAdmin: user.isAdmin
            }
        });

    } catch (error) {
        console.error('Erro no login:', error);
        res.status(500).json({ message: 'Erro interno do servidor.' });
    }
});

// Middleware de autenticação melhorado
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    
    if (!authHeader) {
        console.log('Nenhum header de autorização encontrado');
        return res.status(401).json({ message: 'Token não fornecido.' });
    }

    if (!authHeader.startsWith('Bearer ')) {
        console.log('Formato de token inválido');
        return res.status(401).json({ message: 'Formato de token inválido.' });
    }

    const token = authHeader.split(' ')[1];
    
    jwt.verify(token, JWT_SECRET, (err, decoded) => {
        if (err) {
            console.log('Erro na verificação do token:', err.message);
            return res.status(403).json({ 
                message: 'Token inválido ou expirado.',
                error: err.message 
            });
        }
        
        req.user = decoded;
        console.log('Token verificado com sucesso:', decoded);
        next();
    });
}

// Rota de teste de autenticação
app.get('/api/verify-token', authenticateToken, (req, res) => {
    res.json({
        message: 'Token válido',
        user: req.user
    });
});

// Rota de proxy para o chat com o agente Python/Flask
app.post('/api/chat', async (req, res) => { // MODIFIED: Added 'async' keyword here
    console.log('Recebida requisição de chat. Enviando para o serviço Flask...');
    
    const FLASK_API_URL = `http://localhost:${process.env.FLASK_PORT || 5000}`;
    
    try {
        // O corpo da requisição do frontend (req.body) já deve ser { message: "..." }
        // O endpoint do Flask espera exatamente isso.
        const response = await axios.post(`${FLASK_API_URL}/api/chat`, req.body, {
            headers: {
                'Content-Type': 'application/json',
                // Passando o header de autorização para o serviço Flask
                // O middleware authenticateToken já validou o token e o colocou em req.headers.authorization
                'Authorization': req.headers.authorization
            }
        });

        // Repassa a resposta do serviço Flask diretamente para o frontend
        console.log('Resposta recebida do Flask. Enviando para o frontend.');
        res.status(response.status).json(response.data);

    } catch (error) {
        console.error('Erro ao fazer proxy da requisição de chat para o Flask:', error.message);
        if (error.response) {
            // Se o Flask retornou um erro, repassa esse erro
            console.error(`Erro do serviço Flask: ${error.response.status}`, error.response.data);
            res.status(error.response.status).json(error.response.data);
        } else if (error.request) {
            // Se não conseguiu conectar ao Flask
            console.error('Não foi possível conectar ao serviço Flask.');
            res.status(503).json({ message: 'Serviço de chat indisponível. Não foi possível conectar ao backend Python.' });
        } else {
            // Outro erro
            console.error('Erro inesperado na configuração do proxy.');
            res.status(500).json({ message: 'Erro interno ao processar a requisição de chat.' });
        }
    }
});

app.listen(PORT, () => {
    console.log(`Servidor Node.js rodando na porta ${PORT}`);
    console.log(`JWT_SECRET configurado: ${JWT_SECRET ? '✅' : '❌'}`);
});
