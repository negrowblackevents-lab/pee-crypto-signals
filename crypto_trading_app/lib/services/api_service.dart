import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/balance_history.dart';

class ApiService {
  // Load from environment or config
  static const String baseUrl = 'http://127.0.0.1:8000'; // Change in production
  String? _authToken;

  ApiService({String? authToken}) {
    _authToken = authToken;
  }

  void setAuthToken(String token) {
    _authToken = token;
  }

  Future<BalanceHistoryResponse> getPortfolioHistory({int limit = 365}) async {
    if (_authToken == null) {
      throw Exception('Not authenticated. Please login first.');
    }

    try {
      final uri = Uri.parse('$baseUrl/user/portfolio/history?limit=$limit');
      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $_authToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        return BalanceHistoryResponse.fromJson(json);
      } else if (response.statusCode == 401) {
        throw Exception('Unauthorized. Token may have expired.');
      } else if (response.statusCode == 404) {
        throw Exception('Portfolio history not found.');
      } else {
        throw Exception('Failed to fetch portfolio history: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching portfolio history: $e');
    }
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        _authToken = json['access_token'] as String;
        return json;
      } else {
        throw Exception('Login failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error during login: $e');
    }
  }

  Future<Map<String, dynamic>> register(String email, String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Registration failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error during registration: $e');
    }
  }
}
