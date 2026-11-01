# 📡 Qwenn-RPC - Guia de Utilização

## Visão Geral
Integração Anvil/RPC para dados de mercado em tempo real.
Fetch market data from Anvil/Ethereum RPC → QwenBend generation → strategy execution → results pipeline.

## 🚀 Quick Start

### Instalação
```bash
# Clonar repositório
git clone git@github.com:developerfred/qwenn-rpc.git
cd qwenn-rpc

# Instalar dependências
pip install -r requirements.txt
```

### Fetch Dados de Mercado do Anvil
```python
from qwenn_rpc.anvil_client import fetch_block_data

# Buscar dados do bloco mais recente
data = fetch_block_data()

print(f"Block: {data['block']}")
print(f"Timestamp: {data['timestamp']}")
print(f"ETH Price: ${data['eth_price']}")
# Output:
# Block: 12345678
# Timestamp: 1700000000
# ETH Price: $1850.50
```

### Buscar Dados Específicos
```python
from qwenn_rpc.anvil_client import fetch_block_data, get_block_by_number, get_eth_price

# 1. Buscar bloco por número
block_data = get_block_by_number(12345678)
print(f"Bloco {block_data['block']}: {block_data['timestamp']}")

# 2. Buscar preço ETH
eth_price = get_eth_price()
print(f"Preço ETH atual: ${eth_price}")

# 3. Converter para U32 (formato BendLite)
from qwenn_rpc.anvil_client import price_to_u32, timestamp_to_u32
u32_price = price_to_u32(eth_price)
u32_timestamp = timestamp_to_u32(1700000000)
print(f"U32 Price: {u32_price}")
print(f"U32 Timestamp: {u32_timestamp}")
```

## 🏗️ RPC Endpoints

### Anvil Local (Desenvolvimento)
```
URL: http://127.0.0.1:8545
```

### Endpoints Disponíveis

| Endpoint | Descrição | Exemplo |
|----------|-----------|---------|
| `eth_blockNumber` | Número do bloco mais recente | `0x1234567` |
| `eth_getBlockByNumber` | Dados do bloco por número | `0x1234567` (hex) |
| `eth_getPrice` | Preço ETH em USD (custom) | Retorna float |
| `eth_blockNumber` | Número do bloco | `0x12345678` |

### Exemplos de Chamada

```python
from qwenn_rpc.anvil_client import AnvilClient

client = AnvilClient(url="http://127.0.0.1:8545")

# 1. Número do bloco mais recente
block_number = client.eth_block_number()
print(f"Bloco atual: {block_number}")

# 2. Dados do bloco por número
block_data = client.eth_get_block_by_number("latest", full_transactions=False)
print(f"Timestamp: {block_data['timestamp']}")
print(f"Número: {block_data['block']}")

# 3. Preço ETH
eth_price = client.get_eth_price()
print(f"ETH Price: ${eth_price}")
```

## 📊 Integração com QwenBend

### Converter Dados para Formato BendLite

```python
from qwenn_rpc.anvil_client import fetch_block_data, price_to_u32, timestamp_to_u32
from qwenn_indicators.indicators import rsi, signal_from_rsi

# 1. Buscar dados do Anvil
data = fetch_block_data()
print(f"Block: {data['block']}")
print(f"Timestamp: {data['timestamp']}")
print(f"ETH Price: ${data['eth_price']}")

# 2. Converter para U32 (formato BendLite)
u32_price = price_to_u32(data['eth_price'])
u32_timestamp = timestamp_to_u32(data['timestamp'])

print(f"U32 Price: {u32_price}")
print(f"U32 Timestamp: {u32_timestamp}")

# 3. Calcular RSI de série de preços
# Exemplo: série de preços dos últimos 14 blocos
price_series = [data['eth_price']] * 14  # Simplificado
prices_u32 = [price_to_u32(p) for p in price_series]

# Nota: RSI com U32 usa aritmética inteira exata
# rsi_val = rsi(prices_u32, period=14)
# sinal = signal_from_rsi(rsi_val)
```

### Pipeline Completo: RPC → Qwen → Verificação

```python
from qwenn_rpc.anvil_client import fetch_block_data
from qwenn_strategies.strategy_gen import generate_strategy, verify_strategy
from qwenn_indicators.indicators import rsi, signal_from_rsi

# Step 1: Buscar dados do Anvil
block_data = fetch_block_data()
print(f"📡 Dados Anvil:")
print(f"   Block: {block_data['block']}")
print(f"   Timestamp: {block_data['timestamp']}")
print(f"   ETH Price: ${block_data['eth_price']}")

# Step 2: Gerar estratégia BendLite
strategy_program = generate_strategy(
    market_data=f"ETH/USD: {block_data['eth_price']}, Block {block_data['block']}",
    strategy_type="rsi",
    parameters={"period": 14, "overbought": 70, "oversold": 30}
)

print(f"\n📝 Estratégia Gerada: {len(strategy_program)} chars")

# Step 3: Verificar compliance Bend2
verify_result = verify_strategy(strategy_program)
print(f"\n🔍 Bend2 Verification:")
print(f"   Valid: {verify_result['valid']}")
print(f"   Errors: {len(verify_result['errors'])}")

# Step 4: Executar estratégia
execute_result = execute_strategy(strategy_program, f"{block_data['eth_price']},{block_data['block']}")
print(f"\n⚡ Execução:")
print(f"   Success: {execute_result['success']}")
print(f"   Compliance: {execute_result['compliance']}")
print(f"   Result: {execute_result['result']}")
```

## 🛠️ Classe AnvilClient

### Métodos Disponíveis

```python
from qwenn_rpc.anvil_client import AnvilClient

client = AnvilClient(url="http://127.0.0.1:8545")

# 1. eth_blockNumber
block_number = client.eth_block_number()
# Retorna: int (ex: 12345678)

# 2. eth_getBlockByNumber
block_data = client.eth_get_block_by_number("latest")
# Retorna: dict com {
#   "block": int,
#   "timestamp": int, 
#   "eth_price": float
# }

# 3. get_eth_price()
eth_price = client.get_eth_price()
# Retorna: float (ex: 1850.50)

# 4. timestamp_to_u32(timestamp)
u32_ts = client.timestamp_to_u32(1700000000)
# Retorna: int (formato U32)

# 5. price_to_u32(price)
u32_price = client.price_to_u32(1850.50)
# Retorna: int (formato U32)

# 6. block_to_u32(block_data)
u32_block = client.block_to_u32(block_data)
# Retorna: int

# 7. validate_u32_range(u32_value, min_val, max_val)
is_valid = client.validate_u32_range(2**31, 0, 2**32)
# Retorna: bool

# 8. format_market_data_for_bend(price, timestamp)
formatted = client.format_market_data_for_bend(1850.50, 1700000000)
# Retorna: dict com dados formatados para BendLite
```

### Exemplos Detalhados

#### Obter e Formatando Dados de Mercado
```python
from qwenn_rpc.anvil_client import AnvilClient

client = AnvilClient("http://127.0.0.1:8545")

# Buscar bloco mais recente
block_data = client.eth_get_block_by_number("latest")

# Format para BendLite input
formatted = client.format_market_data_for_bend(
    block_data['eth_price'], 
    block_data['timestamp']
)

print(f"Preço Original: ${block_data['eth_price']}")
print(f"Timestamp Original: {block_data['timestamp']}")
print(f"Preço U32: {formatted['price_u32']}")
print(f"Timestamp U32: {formatted['timestamp_u32']}")
print(f"Block Number: {formatted['block_number']}")
```

#### Converter Série de Preços para RSI
```python
from qwenn_rpc.anvil_client import AnvilClient, price_to_u32, timestamp_to_u32
from qwenn_indicators.indicators import rsi, signal_from_rsi

client = AnvilClient("http://127.0.0.1:8545")

# Buscar últimos 14 blocos com preços
price_series = []
timestamps = []

for i in range(14):
    # Buscar bloco i blocos atrás
    block_num = client.eth_block_number() - i
    block_data = client.eth_get_block_by_number(hex(block_num))
    
    price = block_data['eth_price']
    timestamp = block_data['timestamp']
    
    price_series.append(price)
    timestamps.append(timestamp)

# Converter para U32
prices_u32 = [price_to_u32(p) for p in price_series]
timestamps_u32 = [timestamp_to_u32(t) for t in timestamps]

# Calcular RSI exacto
rsi_val = rsi(prices_u32, period=14)
sinal = signal_from_rsi(rsi_val)

print(f"Série de preços: {price_series}")
print(f"RSI: {rsi_val} → {sinal}")

if sinal == "BUY":
    print("🟢 Oversold: entrada potencial")
elif sinal == "SELL":
    print("🔴 Overbought: considerar venda")
else:
    print("⚪ Neutro: mercado lateral")
```

## ⚡ Performance

### Timing de Requests

| Operação | Tempo Médio | Observações |
|----------|-------------|-------------|
| `eth_blockNumber` | < 10ms | Mais rápido |
| `eth_getBlockByNumber` | 20-50ms | Busca de dados completos |
| `get_eth_price` | 30-100ms | Custom endpoint |
| `fetch_block_data` (completo) | 50-150ms | Todos os dados em um request |

### Otimizações

```python
from qwenn_rpc.anvil_client import AnvilClient
import time

client = AnvilClient("http://127.0.0.1:8545")

# Cache local para evitar requests repetidos
last_block = None
last_fetch = 0
CACHE_TTL = 5  # segundos

def get_market_data_cached():
    global last_block, last_fetch
    
    now = time.time()
    if now - last_fetch < CACHE_TTL and last_block is not None:
        return last_block  # Usar cache
    
    # Fetch novo dados
    data = fetch_block_data()
    last_block = data
    last_fetch = now
    return data

# Usar a cada 5 segundos mínimo
data = get_market_data_cached()
```

## 🔧 Solução de Problemas

### Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `ConnectionError: Unable to connect` | Anvil não está rodando | Iniciar Anvil: `anvil --port 8545` |
| `Method not found` | Endpoint não suportado | Verificar versão do Anvil |
| `Invalid U32 value` | Valor fora de range U32 (0 a 2^32) | Verificar conversão de preço/timestamp |
| `Timeout exceeded` | Anvil lento ou sobrecarregado | Aumentar timeout ou aguardar |

### Debugging

```python
from qwenn_rpc.anvil_client import AnvilClient

client = AnvilClient("http://127.0.0.1:8545")

# Habilitar modo debug
try:
    block = client.eth_block_number()
    print(f"Bloco: {block}")
except Exception as e:
    print(f"❌ Erro: {e}")
    # Verificar se Anvil está rodando
    import subprocess
    subprocess.run(["anvil", "--port", "8545"], capture_output=True)
```

## 📁 Estrutura do Repositório
```
qwenn-rpc/
├── qwenn_rpc/                 # Módulo Python principal
│   ├── __init__.py
│   ├── anvil_client.py        # Cliente Anvil RPC
│   └── market_data.py         # Processamento de dados de mercado
├── tests/                     # Testes unitários (10 testes)
├── pyproject.toml             # Configuração do projeto
├── README.md                  # Documentação principal
├── USAGE_GUIDE.md             # Este guia (novo)
└── docs/                      # Documentação adicional (opcional)
```

## 🧪 Testes

```bash
# Executar todos os testes
python3 -m pytest tests/

# Expected output:
============================= test session starts ==============================
platform darwin -- Python 3.14.1, pytest-9.0.2, pluggy-1.6.0 -- /opt/homebrew/Cellar/python@3.14/3.14.1/lib/python3.14/bin/python3.14
cachedir: .pytest_cache
rootdir: /Volumes/MASS/qwenn-rpc
configfile: pyproject.toml
plugins: anyio-4.12.0, asyncio-1.3.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 10 items

tests/test_rpc.py::test_anvil_client_creation PASSED                     [ 10%]
tests/test_rpc.py::test_price_to_u32 PASSED                              [ 20%]
tests/test_rpc.py::test_timestamp_to_u32 PASSED                          [ 30%]
tests/test_rpc.py::test_block_to_u32 PASSED                              [ 40%]
tests/test_rpc.py::test_validate_u32_range PASSED                        [ 50%]
tests/test_rpc.py::test_format_market_data_for_bend PASSED                 [ 60%]
tests/test_rpc.py::test_format_price_series_for_rsi PASSED                 [ 70%]
tests/test_rpc.py::test_pipeline_price_momentum PASSED                   [ 80%]
tests/test_rpc.py::test_get_market_data_from_anvil_structure PASSED          [ 90%]
tests/test_rpc.py::test_rpc_error_classes PASSED                         [100%]

============================== 10 passed in 0.36s ==============================
```

## 🚀 Casos de Uso

### 1. Trading Algorítmico em Tempo Real
```python
import time
from qwenn_rpc.anvil_client import AnvilClient
from qwenn_indicators.indicators import rsi, signal_from_rsi

client = AnvilClient("http://127.0.0.1:8545")

while True:
    # Buscar dados a cada 15 segundos
    data = client.fetch_block_data()
    
    # Converter para U32
    prices_u32 = [price_to_u32(data['eth_price'])] * 14  # Série simplificada
    
    # Calcular RSI
    rsi_val = rsi(prices_u32, period=14)
    sinal = signal_from_rsi(rsi_val)
    
    print(f"[{time.strftime('%H:%M:%S')}] RSI: {rsi_val} → {sinal}")
    
    if sinal == "BUY":
        print("🟢 Sinal de COMPRA detectado!")
    elif sinal == "SELL":
        print("🔴 Sinal de VENDA detectado!")
    
    time.sleep(15)
```

### 2. Análise Histórica
```python
from qwenn_rpc.anvil_client import AnvilClient
from qwenn_indicators.indicators import rsi

client = AnvilClient("http://127.0.0.1:8545")

# Buscar últimos 100 blocos para análise histórica
block_numbers = range(client.eth_block_number() - 100, client.eth_block_number())
prices = []
timestamps = []

for bn in block_numbers:
    data = client.eth_get_block_by_number(hex(bn))
    prices.append(data['eth_price'])
    timestamps.append(data['timestamp'])

# Calcular RSI da série histórica
# (Necessário reverter a lista para ordem cronológica)
prices_reversed = prices[::-1]
timestamps_reversed = timestamps[::-1]

# Converter para U32 e calcular
prices_u32 = [price_to_u32(p) for p in prices_reversed]
rsi_val = rsi(prices_u32, period=14)
print(f"RSI histórico (últimos 100 blocos): {rsi_val}")
```

### 3. Integração com Estratégia BendLite
```python
from qwenn_rpc.anvil_client import fetch_block_data
from qwenn_strategies.strategy_gen import generate_strategy, verify_strategy

# Buscar dados atuais
block_data = fetch_block_data()

# Gerar estratégia baseada em dados reais
strategy = generate_strategy(
    market_data=f"ETH at ${block_data['eth_price']}, Block {block_data['block']}",
    strategy_type="rsi",
    parameters={"period": 14, "overbought": 70, "oversold": 30}
)

# Verificar compliance
verify = verify_strategy(strategy)
print(f"Strategy compliant: {verify['valid']}")

if verify['valid']:
    print("✅ Strategy approved - ready for execution")
else:
    print(f"❌ {len(verify['errors'])} errors - review before execution")
```

## ⚠️ Considerações Importantes

### Anvil vs Mainnet
- **Anvil:** Local de desenvolvimento, dados simulados/fake, sem custos de gas
- **Mainnet:** Mainnet da Ethereum, dados reais, custos de gas aplicáveis
- **Recomendação:** Usar Anvil para desenvolvimento e testing, Mainnet apenas com API keys legitimadas

### Segurança
- Nunca exponha chaves privadas em código que consome RPC
- Os endpoints RPC expostos aqui são de leitura apenas (read-only)
- Dados de preço podem ter delay de alguns segundos

### Limites de Rate
- Anvil local: Sem limites rígidos, mas não fazer requests em loop sem pausa
- Mainnet via Infura/Alchemy: Limites dependem do plano (free: ~50 req/min)

## 🆘 Suporte

- **Issues:** GitHub Issues do repositório
- **Discussions:** Discussions na aba Discussions
- **Anvil Help:** [Anvil Documentation](https://anvil-foundry.github.io/)
- **Email:** codingsh@pm.me

## 📜 Licença
Apache-2.0 - See LICENSE file for details.