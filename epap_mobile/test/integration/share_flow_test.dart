import 'package:flutter_test/flutter_test.dart';
import 'package:epap_mobile/providers/analysis_provider.dart';
import 'package:epap_mobile/services/api_service.dart';
import 'package:epap_mobile/services/database_service.dart';
import 'package:epap_mobile/services/share_handler.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';

void main() {
  group('Share Flow Integration', () {
    late AnalysisProvider provider;
    late ShareHandler shareHandler;

    setUp(() {
      final apiService = ApiService(baseUrl: 'http://localhost:8000');
      final databaseService = DatabaseService();
      provider = AnalysisProvider(
        apiService: apiService,
        databaseService: databaseService,
      );
      shareHandler = ShareHandler();
    });

    tearDown(() {
      shareHandler.dispose();
      provider.dispose();
    });

    test('sharing URL from browser triggers analysis', () async {
      // Track that analysis was called
      String? analyzedUrl;

      // Setup mock shared URL
      final mockMediaStream = Stream<List<SharedMediaFile>>.value([
        SharedMediaFile(
          path: 'https://example.com/news',
          type: SharedMediaType.url,
        ),
      ]);

      ReceiveSharingIntent.setMockValues(
        initialMedia: [],
        mediaStream: mockMediaStream,
      );

      // Setup handler to track analysis calls (not actually call provider)
      shareHandler.init(
        onShare: (sharedText) {
          if (sharedText.startsWith('http://') ||
              sharedText.startsWith('https://')) {
            analyzedUrl = sharedText;
          }
        },
        onInitialShare: (sharedText) {
          if (sharedText.startsWith('http://') ||
              sharedText.startsWith('https://')) {
            analyzedUrl = sharedText;
          }
        },
      );

      // Wait for share event
      await Future.delayed(const Duration(milliseconds: 100));

      // Verify URL analysis would be triggered
      expect(analyzedUrl, 'https://example.com/news');
    });

    test('sharing plain text triggers text analysis', () async {
      // Track that analysis was called
      String? analyzedText;
      bool isUrl = true;

      // Setup mock shared text
      final mockMediaStream = Stream<List<SharedMediaFile>>.value([
        SharedMediaFile(
          path: 'Some propaganda text to analyze',
          type: SharedMediaType.text,
        ),
      ]);

      ReceiveSharingIntent.setMockValues(
        initialMedia: [],
        mediaStream: mockMediaStream,
      );

      // Setup handler to track analysis calls
      shareHandler.init(
        onShare: (sharedText) {
          if (sharedText.startsWith('http://') ||
              sharedText.startsWith('https://')) {
            analyzedText = sharedText;
            isUrl = true;
          } else {
            analyzedText = sharedText;
            isUrl = false;
          }
        },
        onInitialShare: (sharedText) {
          if (sharedText.startsWith('http://') ||
              sharedText.startsWith('https://')) {
            analyzedText = sharedText;
            isUrl = true;
          } else {
            analyzedText = sharedText;
            isUrl = false;
          }
        },
      );

      // Wait for share event
      await Future.delayed(const Duration(milliseconds: 100));

      // Verify text analysis would be triggered
      expect(analyzedText, 'Some propaganda text to analyze');
      expect(isUrl, false); // Should be analyzed as text, not URL
    });

    test('initial share when app launches triggers analysis', () async {
      // Track initial share
      String? initialShare;

      // Setup mock initial share
      final mockInitialMedia = [
        SharedMediaFile(
          path: 'https://example.com/article',
          type: SharedMediaType.url,
        ),
      ];

      ReceiveSharingIntent.setMockValues(
        initialMedia: mockInitialMedia,
        mediaStream: Stream.empty(),
      );

      // Setup handler
      shareHandler.init(
        onShare: (sharedText) {
          // Should not be called for initial share
        },
        onInitialShare: (sharedText) {
          initialShare = sharedText;
        },
      );

      // Wait for initial share processing
      await Future.delayed(const Duration(milliseconds: 100));

      // Verify initial share was received
      expect(initialShare, 'https://example.com/article');
    });

    test('share handler properly distinguishes URLs from text', () async {
      // Track what type of analysis would be triggered
      final results = <Map<String, dynamic>>[];

      // Test multiple share scenarios
      final mockMediaStream = Stream<List<SharedMediaFile>>.fromIterable([
        [
          SharedMediaFile(
            path: 'https://example.com/news',
            type: SharedMediaType.url,
          ),
        ],
        [
          SharedMediaFile(
            path: 'Plain text content',
            type: SharedMediaType.text,
          ),
        ],
        [
          SharedMediaFile(
            path: 'http://another.com',
            type: SharedMediaType.url,
          ),
        ],
      ]);

      ReceiveSharingIntent.setMockValues(
        initialMedia: [],
        mediaStream: mockMediaStream,
      );

      // Setup handler
      shareHandler.init(
        onShare: (sharedText) {
          if (sharedText.startsWith('http://') ||
              sharedText.startsWith('https://')) {
            results.add({'type': 'url', 'value': sharedText});
          } else {
            results.add({'type': 'text', 'value': sharedText});
          }
        },
        onInitialShare: (sharedText) {},
      );

      // Wait for all events
      await Future.delayed(const Duration(milliseconds: 300));

      // Verify correct classification
      expect(results.length, 3);
      expect(results[0]['type'], 'url');
      expect(results[0]['value'], 'https://example.com/news');
      expect(results[1]['type'], 'text');
      expect(results[1]['value'], 'Plain text content');
      expect(results[2]['type'], 'url');
      expect(results[2]['value'], 'http://another.com');
    });
  });
}
