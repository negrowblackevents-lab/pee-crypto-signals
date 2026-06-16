class BalanceHistoryItem {
  final DateTime timestamp;
  final double balanceUsdt;
  final double pnl24h;
  final int positionsCount;

  BalanceHistoryItem({
    required this.timestamp,
    required this.balanceUsdt,
    required this.pnl24h,
    required this.positionsCount,
  });

  factory BalanceHistoryItem.fromJson(Map<String, dynamic> json) {
    return BalanceHistoryItem(
      timestamp: DateTime.parse(json['timestamp'] as String),
      balanceUsdt: (json['balance_usdt'] as num).toDouble(),
      pnl24h: (json['pnl_24h'] as num).toDouble(),
      positionsCount: json['positions_count'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'balance_usdt': balanceUsdt,
      'pnl_24h': pnl24h,
      'positions_count': positionsCount,
    };
  }
}

class BalanceHistoryResponse {
  final int userId;
  final List<BalanceHistoryItem> items;
  final double currentBalance;

  BalanceHistoryResponse({
    required this.userId,
    required this.items,
    required this.currentBalance,
  });

  factory BalanceHistoryResponse.fromJson(Map<String, dynamic> json) {
    return BalanceHistoryResponse(
      userId: json['user_id'] as int,
      items: (json['items'] as List<dynamic>)
          .map((item) => BalanceHistoryItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      currentBalance: (json['current_balance'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'items': items.map((item) => item.toJson()).toList(),
      'current_balance': currentBalance,
    };
  }
}
