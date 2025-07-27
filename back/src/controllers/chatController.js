const axios = require('axios');

exports.chatWithEvoAI = async (req, res) => {
  try {
    const { message } = req.body;
    
    const response = await axios.post(process.env.EVO_AI_AGENT_BASE_URL, {
      jsonrpc: "2.0",
      method: "message/send",
      params: {
        message: {
          role: "user",
          parts: [{ type: "text", text: message }]
        }
      }
    }, {
      headers: {
        'x-api-key': process.env.EVO_AI_API_KEY
      }
    });

    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};