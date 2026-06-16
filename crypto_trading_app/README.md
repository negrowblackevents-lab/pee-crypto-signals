# Crypto Trading App - Flutter Frontend

A Flutter mobile app for visualizing crypto trading portfolio performance with real-time balance tracking and historical charts.

## Features

- 📊 **Balance History Chart** - Visual representation of portfolio balance over time
- 📈 **Performance Metrics** - Track highest, lowest, and current balance
- ⏱️ **Time Range Selection** - View 7, 30, 90, or 365 days of history
- 🔐 **Secure Authentication** - JWT-based token authentication with backend
- 📱 **Responsive UI** - Clean Material Design interface

## Prerequisites

1. **Flutter SDK** installed (version 3.0.0 or later)
   - Download from: https://flutter.dev/docs/get-started/install
   
2. **Dart** (comes with Flutter)

3. **Backend API** running
   - Default: `http://127.0.0.1:8000`
   - See [../README.md](../README.md) for backend setup

## Setup Instructions

### 1. Install Dependencies

```bash
cd crypto_trading_app
flutter pub get
```

### 2. Update API Configuration

Edit `lib/services/api_service.dart` and update the `baseUrl` if needed:

```dart
static const String baseUrl = 'http://127.0.0.1:8000'; // Production: https://your-api.com
```

### 3. Run the App

**Development:**
```bash
flutter run
```

**Release Build:**
```bash
flutter build apk    # Android
flutter build ios    # iOS
```

## API Integration

### Authentication Flow

1. User logs in via `/auth/login` endpoint
2. Backend returns JWT access token
3. Token stored in `ApiService` instance
4. All subsequent requests include token in `Authorization` header

### Portfolio History Endpoint

```
GET /user/portfolio/history?limit=365
Authorization: Bearer {jwt_token}

Response:
{
  "user_id": 1,
  "items": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "balance_usdt": 10000.50,
      "pnl_24h": 250.0,
      "positions_count": 3
    }
  ],
  "current_balance": 10250.75
}
```

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── screens/
│   └── portfolio_screen.dart # Portfolio with chart visualization
├── models/
│   └── balance_history.dart  # Data models (BalanceHistoryResponse, BalanceHistoryItem)
└── services/
    └── api_service.dart      # API client for backend communication

```

## Key Dependencies

- **fl_chart** (^0.68.0) - Beautiful charts for Flutter
- **http** (^1.2.0) - HTTP client for API communication
- **provider** (^6.4.0) - State management (optional)
- **flutter_secure_storage** (^9.0.0) - Secure token storage

## Environment Variables

Create a `.env` file in the project root (optional):

```
BACKEND_API_BASE_URL=http://127.0.0.1:8000
```

## Development Notes

### Adding More Screens

1. Create new screen file in `lib/screens/`
2. Add route in `main.dart` navigation
3. Use `ApiService` for backend communication

### Extending API Client

Add new methods to `ApiService` for:
- Trading endpoints
- Signal history
- Account settings
- Device management

### State Management

Currently using simple `FutureBuilder`. For complex state, migrate to:
- Provider (already in dependencies)
- Riverpod
- BLoC pattern

## Testing

```bash
# Run tests
flutter test

# Test coverage
flutter test --coverage
```

## Build & Deployment

### Android

```bash
flutter build apk --release
flutter build appbundle --release  # For Play Store
```

### iOS

```bash
flutter build ios --release
# Then use Xcode for App Store upload
```

### Web (Optional)

```bash
flutter build web --release
```

## Troubleshooting

### API Connection Issues

- Verify backend is running on configured URL
- Check firewall/network settings
- Ensure CORS is enabled on backend

### Chart Not Displaying

- Verify API returns data with proper format
- Check timestamp parsing (ISO 8601 format required)
- Ensure balance values are numeric

### Authentication Errors

- Token may have expired - re-login required
- Check backend JWT secret configuration
- Verify token is stored correctly after login

## Security Considerations

1. **Token Storage** - Currently stores in memory; for production, use `flutter_secure_storage`
2. **HTTPS** - Use HTTPS in production
3. **Environment Secrets** - Use proper secret management, not hardcoded values
4. **API Validation** - Validate all API responses

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push branch: `git push origin feature/your-feature`
4. Create Pull Request

## License

MIT License - See LICENSE file in project root

## Support

For issues or questions:
1. Check existing GitHub Issues
2. Review API documentation in main README.md
3. Check backend logs for API errors

