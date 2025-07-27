interface Signal {
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  entry_time: string;
  target_price: number;
  projection_percentage: number;
  signal_class: 'PREMIUM' | 'ELITE' | 'PADRÃO';
  status: string;
}

// ... existing code ...

// No mapeamento dos SignalCards:
{!loading && !error && signals.length > 0 && signals.map((signal, index) => (
  <SignalCard
    key={index}
    symbol={signal.symbol}
    type={signal.type}
    entryPrice={String(signal.entry_price)}
    targetPrice={String(signal.target_price)}
    projectionPercentage={String(signal.projection_percentage)}
    date={signal.entry_time}
    signalClass={signal.signal_class}
  />
))}