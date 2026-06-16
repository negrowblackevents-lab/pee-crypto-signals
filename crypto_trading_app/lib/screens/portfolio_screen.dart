import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';
import '../models/balance_history.dart';

class PortfolioScreen extends StatefulWidget {
  const PortfolioScreen({Key? key}) : super(key: key);

  @override
  State<PortfolioScreen> createState() => _PortfolioScreenState();
}

class _PortfolioScreenState extends State<PortfolioScreen> {
  late ApiService apiService;
  late Future<BalanceHistoryResponse> balanceHistoryFuture;
  int selectedDaysLimit = 30;

  @override
  void initState() {
    super.initState();
    apiService = ApiService();
    balanceHistoryFuture = apiService.getPortfolioHistory(limit: selectedDaysLimit);
  }

  void _refreshData(int newLimit) {
    setState(() {
      selectedDaysLimit = newLimit;
      balanceHistoryFuture = apiService.getPortfolioHistory(limit: newLimit);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Portfolio Performance'),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Time range selector
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildTimeButton('7D', 7),
                  _buildTimeButton('30D', 30),
                  _buildTimeButton('90D', 90),
                  _buildTimeButton('365D', 365),
                ],
              ),
            ),
            // Chart
            FutureBuilder<BalanceHistoryResponse>(
              future: balanceHistoryFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Padding(
                    padding: EdgeInsets.all(32.0),
                    child: CircularProgressIndicator(),
                  );
                } else if (snapshot.hasError) {
                  return Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Text('Error: ${snapshot.error}'),
                  );
                } else if (snapshot.hasData) {
                  return _buildBalanceChart(snapshot.data!);
                } else {
                  return const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Text('No data available'),
                  );
                }
              },
            ),
            // Stats section
            FutureBuilder<BalanceHistoryResponse>(
              future: balanceHistoryFuture,
              builder: (context, snapshot) {
                if (snapshot.hasData) {
                  return _buildStatsSection(snapshot.data!);
                }
                return const SizedBox.shrink();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeButton(String label, int days) {
    final isSelected = selectedDaysLimit == days;
    return ElevatedButton(
      onPressed: () => _refreshData(days),
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected ? Colors.blue : Colors.grey[300],
        foregroundColor: isSelected ? Colors.white : Colors.black,
      ),
      child: Text(label),
    );
  }

  Widget _buildBalanceChart(BalanceHistoryResponse data) {
    if (data.items.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(32.0),
        child: Text('No historical data available yet'),
      );
    }

    final spots = data.items
        .asMap()
        .entries
        .map((entry) => FlSpot(entry.key.toDouble(), entry.value.balanceUsdt))
        .toList();

    final minBalance = data.items.map((item) => item.balanceUsdt).reduce((a, b) => a < b ? a : b);
    final maxBalance = data.items.map((item) => item.balanceUsdt).reduce((a, b) => a > b ? a : b);

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Container(
        height: 300,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: Colors.grey[100],
        ),
        child: LineChart(
          LineChartData(
            gridData: const FlGridData(show: true),
            titlesData: const FlTitlesData(
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(showTitles: false),
              ),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(showTitles: true, reservedSize: 40),
              ),
            ),
            borderData: FlBorderData(show: true),
            minX: 0,
            maxX: (data.items.length - 1).toDouble(),
            minY: minBalance - 100,
            maxY: maxBalance + 100,
            lineBarsData: [
              LineChartBarData(
                spots: spots,
                isCurved: true,
                color: Colors.blue,
                barWidth: 2,
                dotData: const FlDotData(show: false),
                belowBarData: BarAreaData(
                  show: true,
                  color: Colors.blue.withOpacity(0.1),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatsSection(BalanceHistoryResponse data) {
    if (data.items.isEmpty) {
      return const SizedBox.shrink();
    }

    final firstBalance = data.items.first.balanceUsdt;
    final lastBalance = data.items.last.balanceUsdt;
    final change = lastBalance - firstBalance;
    final changePercent = (change / firstBalance) * 100;

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Divider(),
          const SizedBox(height: 8),
          const Text('Statistics', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStatCard('Current Balance', '\$${data.currentBalance.toStringAsFixed(2)}'),
              _buildStatCard('Change', '\$${change.toStringAsFixed(2)} (${changePercent.toStringAsFixed(2)}%)'),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStatCard('Highest', '\$${data.items.map((i) => i.balanceUsdt).reduce((a, b) => a > b ? a : b).toStringAsFixed(2)}'),
              _buildStatCard('Lowest', '\$${data.items.map((i) => i.balanceUsdt).reduce((a, b) => a < b ? a : b).toStringAsFixed(2)}'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              const SizedBox(height: 8),
              Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ),
    );
  }
}
