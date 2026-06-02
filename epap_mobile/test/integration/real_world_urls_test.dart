import 'package:flutter_test/flutter_test.dart';
import 'package:epap_mobile/services/share_handler.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';

/// Tests with real-world URLs from Greek news sites
/// These test that the app can handle actual URLs users would share
void main() {
  group('Real World URLs', () {
    late ShareHandler shareHandler;
    late List<String> receivedUrls;

    setUp(() {
      shareHandler = ShareHandler();
      receivedUrls = [];
    });

    tearDown(() {
      shareHandler.dispose();
    });

    test('handles DocumentoNews article URL', () async {
      // DocumentoNews.gr - known for biased political coverage
      const articleUrl =
          'https://www.documentonews.gr/article/varoufakis-kata-tsipra-to-soufle-den-fouskonei-dyo-fores-efthynetai-pou-apetychan-ta-aristera-kommata/';

      final mockMediaStream = Stream<List<SharedMediaFile>>.value([
        SharedMediaFile(
          path: articleUrl,
          type: SharedMediaType.url,
        ),
      ]);

      ReceiveSharingIntent.setMockValues(
        initialMedia: [],
        mediaStream: mockMediaStream,
      );

      shareHandler.init(
        onShare: (url) => receivedUrls.add(url),
        onInitialShare: (url) => receivedUrls.add(url),
      );

      await Future.delayed(const Duration(milliseconds: 100));

      expect(receivedUrls.length, 1);
      expect(receivedUrls.first, articleUrl);
      expect(receivedUrls.first.startsWith('https://'), true);
    });

    test('handles long Greek URLs with special characters', () async {
      // URLs with Greek text in path (URL-encoded or not)
      const urls = [
        'https://www.documentonews.gr/article/varoufakis-kata-tsipra-to-soufle-den-fouskonei-dyo-fores-efthynetai-pou-apetychan-ta-aristera-kommata/',
        'https://www.protothema.gr/politics/article/1234567/syriza-nd-pasok/',
        'https://www.kathimerini.gr/politics/562345678/article-with-greek-text/',
      ];

      for (final url in urls) {
        receivedUrls.clear();

        final mockMediaStream = Stream<List<SharedMediaFile>>.value([
          SharedMediaFile(
            path: url,
            type: SharedMediaType.url,
          ),
        ]);

        ReceiveSharingIntent.setMockValues(
          initialMedia: [],
          mediaStream: mockMediaStream,
        );

        shareHandler.init(
          onShare: (sharedUrl) => receivedUrls.add(sharedUrl),
          onInitialShare: (sharedUrl) => receivedUrls.add(sharedUrl),
        );

        await Future.delayed(const Duration(milliseconds: 100));

        expect(receivedUrls.length, 1,
            reason: 'Should receive URL: $url');
        expect(receivedUrls.first, url);

        shareHandler.dispose();
        shareHandler = ShareHandler();
      }
    });

    test('handles URLs from various Greek news sites', () async {
      // Common Greek news sites that might be shared
      const newsUrls = [
        'https://www.documentonews.gr/article/some-article/',
        'https://www.kathimerini.gr/politics/article/',
        'https://www.protothema.gr/greece/news/',
        'https://www.tovima.gr/politics/article/',
        'https://www.iefimerida.gr/news/',
        'https://www.news247.gr/politiki/',
        'https://www.in.gr/politics/',
      ];

      for (final url in newsUrls) {
        receivedUrls.clear();

        final mockMediaStream = Stream<List<SharedMediaFile>>.value([
          SharedMediaFile(
            path: url,
            type: SharedMediaType.url,
          ),
        ]);

        ReceiveSharingIntent.setMockValues(
          initialMedia: [],
          mediaStream: mockMediaStream,
        );

        shareHandler.init(
          onShare: (sharedUrl) => receivedUrls.add(sharedUrl),
          onInitialShare: (sharedUrl) => receivedUrls.add(sharedUrl),
        );

        await Future.delayed(const Duration(milliseconds: 100));

        expect(receivedUrls.length, 1);
        expect(receivedUrls.first, url);
        expect(receivedUrls.first.startsWith('https://'), true);

        shareHandler.dispose();
        shareHandler = ShareHandler();
      }
    });

    test('correctly identifies news URLs vs other URLs', () async {
      final testCases = [
        {
          'url': 'https://www.documentonews.gr/article/test/',
          'isNews': true,
        },
        {
          'url': 'https://www.google.com/search?q=news',
          'isNews': false,
        },
        {
          'url': 'https://www.kathimerini.gr/politics/article/',
          'isNews': true,
        },
        {
          'url': 'https://www.youtube.com/watch?v=123',
          'isNews': false,
        },
      ];

      for (final testCase in testCases) {
        receivedUrls.clear();

        final mockMediaStream = Stream<List<SharedMediaFile>>.value([
          SharedMediaFile(
            path: testCase['url'] as String,
            type: SharedMediaType.url,
          ),
        ]);

        ReceiveSharingIntent.setMockValues(
          initialMedia: [],
          mediaStream: mockMediaStream,
        );

        shareHandler.init(
          onShare: (url) => receivedUrls.add(url),
          onInitialShare: (url) => receivedUrls.add(url),
        );

        await Future.delayed(const Duration(milliseconds: 100));

        expect(receivedUrls.length, 1);
        expect(receivedUrls.first, testCase['url']);

        shareHandler.dispose();
        shareHandler = ShareHandler();
      }
    });

    test('handles URL with query parameters', () async {
      const urlWithParams =
          'https://www.documentonews.gr/article/test/?utm_source=facebook&utm_medium=social';

      final mockMediaStream = Stream<List<SharedMediaFile>>.value([
        SharedMediaFile(
          path: urlWithParams,
          type: SharedMediaType.url,
        ),
      ]);

      ReceiveSharingIntent.setMockValues(
        initialMedia: [],
        mediaStream: mockMediaStream,
      );

      shareHandler.init(
        onShare: (url) => receivedUrls.add(url),
        onInitialShare: (url) => receivedUrls.add(url),
      );

      await Future.delayed(const Duration(milliseconds: 100));

      expect(receivedUrls.length, 1);
      expect(receivedUrls.first, urlWithParams);
      expect(receivedUrls.first.contains('utm_source'), true);
    });

    test('handles URL with fragment', () async {
      const urlWithFragment =
          'https://www.documentonews.gr/article/test/#comments';

      final mockMediaStream = Stream<List<SharedMediaFile>>.value([
        SharedMediaFile(
          path: urlWithFragment,
          type: SharedMediaType.url,
        ),
      ]);

      ReceiveSharingIntent.setMockValues(
        initialMedia: [],
        mediaStream: mockMediaStream,
      );

      shareHandler.init(
        onShare: (url) => receivedUrls.add(url),
        onInitialShare: (url) => receivedUrls.add(url),
      );

      await Future.delayed(const Duration(milliseconds: 100));

      expect(receivedUrls.length, 1);
      expect(receivedUrls.first, urlWithFragment);
      expect(receivedUrls.first.contains('#'), true);
    });
  });
}
