import 'package:flutter/material.dart';
import 'screens/portfolio_screen.dart';

void main() {
  runApp(const CryptoTradingApp());
}

class CryptoTradingApp extends StatelessWidget {
  const CryptoTradingApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Crypto Trading',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const PortfolioScreen(),
    );
  }
}
