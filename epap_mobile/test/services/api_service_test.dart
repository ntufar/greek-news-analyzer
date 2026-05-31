import 'package:flutter_test/flutter_test.dart';
import 'package:epap_mobile/services/api_service.dart';

void main() {
  group('ApiService', () {
    test('analyze returns error result on network failure', () async {
      final service = ApiService(
        baseUrl: 'http://nonexistent.invalid',
      );

      final result = await service.analyze(url: 'https://example.com');

      expect(result.success, false);
      expect(result.error, isNotNull);
    });
  });
}
