import websocket
import json
import requests
import time
from datetime import datetime, timedelta
import os

class BinanceMonitor:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.ws_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_4h"
        self.known_pairs_file = "known_pairs.json"
        self.known_pairs = self.load_known_pairs()
        self.ws = None  # Initialize websocket connection variable

    def format_signal(self, symbol, signal_type, entry_price, tp3_price=None):
        """Formata o sinal no padrão esperado pelo sistema"""
        try:
            formatted_entry_price = float(entry_price)
            formatted_tp3 = float(tp3_price) if tp3_price else formatted_entry_price * 1.02
            
            signal = {
                'symbol': symbol,
                'type': signal_type,
                'entry': str(formatted_entry_price),
                'entry_price': str(formatted_entry_price),
                'tp3': str(formatted_tp3),
                'status': 'OPEN',
                'timeframe': '4h',
                'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'target_exit_time': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
                'exit_price': '0',
                'variation': '0',
                'result': '0'
            }
            # Removido o print de debug do sinal
            return signal
            
        except Exception as e:
            print(f"Erro ao formatar sinal: {e}")
            return None

    def get_latest_data(self, symbol):
        try:
            clean_symbol = symbol.replace('.P', '')
            endpoint = f"/fapi/v1/klines"
            url = f"{self.base_url}{endpoint}"
            
            params = {
                'symbol': clean_symbol,
                'interval': '4h',
                'limit': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    return None
                    
                try:
                    latest_kline = data[-1]
                    close_price = float(latest_kline[4])
                    
                    # Tratamento mais seguro do timestamp
                    try:
                        timestamp = int(latest_kline[0])
                        entry_time = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    signal = {
                        'symbol': clean_symbol,
                        'type': 'LONG',
                        'entry_price': str(close_price),
                        'entry_time': entry_time,
                        'status': 'OPEN',
                        'timeframe': '4h'
                    }
                    
                    return {
                        'symbol': clean_symbol,
                        'data': data,
                        **signal
                    }
                    
                except Exception as e:
                    print(f"Erro no processamento de dados para {clean_symbol}")
                    return None
                    
            return None
            
        except Exception as e:
            print(f"Erro na requisição para {symbol}")
            return None

    def load_known_pairs(self):
        if os.path.exists(self.known_pairs_file):
            with open(self.known_pairs_file, 'r') as f:
                return set(json.load(f))
        return set()

    def get_usdt_pairs(self):
        try:
            # --- Start Edit 1 ---
            # Fetch exchange info to get all USDT symbols
            exchange_info_response = requests.get(self.base_url + "/fapi/v1/exchangeInfo")
            if exchange_info_response.status_code != 200:
                print(f"Error accessing Binance exchange info. Status code: {exchange_info_response.status_code}")
                return set()

            exchange_info_data = exchange_info_response.json()
            all_usdt_pairs = {
                s['symbol'] for s in exchange_info_data['symbols']
                if s['symbol'].endswith('USDT') and s['status'] == 'TRADING'
            }

            # Fetch leverage brackets to get max leverage for each symbol
            leverage_response = requests.get(self.base_url + "/fapi/v1/leverageBracket")
            if leverage_response.status_code != 200:
                print(f"Error accessing Binance leverage info. Status code: {leverage_response.status_code}")
                # If leverage info fails, return all USDT pairs found in exchange info as a fallback
                return all_usdt_pairs

            leverage_data = leverage_response.json()
            # Create a map from symbol to its initial max leverage (from the first bracket)
            leverage_map = {item['symbol']: item['brackets'][0]['initialLeverage'] for item in leverage_data}

            # Filter USDT pairs based on max leverage >= 50
            filtered_pairs = set()
            for symbol in all_usdt_pairs:
                max_leverage = leverage_map.get(symbol, 0) # Get max leverage, default to 0 if not found
                if max_leverage >= 50:
                    filtered_pairs.add(symbol)

            return filtered_pairs
            # --- End Edit 1 ---
        except Exception as e:
            print(f"Error in get_usdt_pairs: {e}")
            return set()

    def preview_pairs(self):
        print("Fetching pairs from Binance...")
        current_pairs = self.get_usdt_pairs()
        if current_pairs:
            print("\nCurrent USDT pairs preview:")
            print(f"Total pairs: {len(current_pairs)}")
            print("\nList of all USDT pairs:")
            for pair in sorted(current_pairs):
                print(pair)
            return True
        else:
            print("Failed to fetch pairs from Binance. Please check your internet connection.")
            return False

    def on_message(self, ws, message):
        data = json.loads(message)
        kline = data['k']
        symbol = kline['s']
        open_price = float(kline['o'])
        close_price = float(kline['c'])
        high_price = float(kline['h'])
        low_price = float(kline['l'])
        volume = float(kline['v'])
        is_closed = kline['x']

        if is_closed:
            print(f"Symbol: {symbol}")
            print(f"Open: {open_price}")
            print(f"Close: {close_price}")
            print(f"High: {high_price}")
            print(f"Low: {low_price}")
            print(f"Volume: {volume}")
            print("------------------------")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def on_open(self, ws):
        print("WebSocket connection opened!")

    def monitor_new_listings(self, interval=120):
        """Monitora novos pares listados na Binance"""
        print("Iniciando monitoramento de novas listagens...")
        try:
            while True:
                current_pairs = self.get_usdt_pairs()
                new_pairs = current_pairs - self.known_pairs
                
                if new_pairs:
                    print("\nNovos pares encontrados:")
                    for pair in new_pairs:
                        print(f"- {pair}")
                    self.known_pairs = current_pairs
                    with open(self.known_pairs_file, 'w') as f:
                        json.dump(list(self.known_pairs), f)
                
                print(f"\nAguardando {interval} segundos...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoramento interrompido pelo usuário")

    def monitor_price(self):
        """Monitora preço do BTC/USDT via WebSocket"""
        try:
            print("Iniciando monitoramento de preço...")
            self.start_websocket()
        except Exception as e:
            print(f"Erro no WebSocket: {e}")
        finally:
            if self.ws:  # Usando self.ws ao invés de ws
                self.ws.close()

    def start_websocket(self):
        """Initialize and start websocket connection"""
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            self.ws.run_forever()
        except Exception as e:
            print(f"Error starting websocket: {e}")

    def stop_websocket(self):
        """Safely close websocket connection"""
        if self.ws:
            self.ws.close()

if __name__ == "__main__":
    monitor = BinanceMonitor()
    try:
        while True:
            print("\nChoose monitoring mode:")
            print("1. Monitor new listings")
            print("2. Monitor BTC/USDT price")
            print("3. Preview current pairs")
            print("4. Exit")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == "4":
                print("Exiting...")
                break
                
            if choice == "1":
                monitor.monitor_new_listings(interval=120)
            elif choice == "2":
                monitor.monitor_price()
            elif choice == "3":
                monitor.preview_pairs()
                input("\nPress Enter to return to menu...")
            else:
                print("Invalid choice!")
                
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        print("\nFinalizando...")