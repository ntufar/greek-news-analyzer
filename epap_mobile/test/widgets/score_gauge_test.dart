import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:epap_mobile/widgets/score_gauge.dart';
import 'package:epap_mobile/utils/constants.dart';

void main() {
  group('ScoreGauge', () {
    testWidgets('displays the score number', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ScoreGauge(score: 85)),
        ),
      );

      expect(find.text('85'), findsOneWidget);
    });

    testWidgets('displays score label for excellent score', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ScoreGauge(score: 85)),
        ),
      );

      expect(find.text('Εξαιρετική'), findsOneWidget);
    });

    testWidgets('displays score label for low score', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ScoreGauge(score: 15)),
        ),
      );

      expect(find.text('Χαμηλή'), findsOneWidget);
    });

    testWidgets('displays score label for medium score', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ScoreGauge(score: 45)),
        ),
      );

      expect(find.text('Μέτρια'), findsOneWidget);
    });

    testWidgets('displays score label for high score', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ScoreGauge(score: 70)),
        ),
      );

      expect(find.text('Υψηλή'), findsOneWidget);
    });

    testWidgets('displays /100 suffix', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ScoreGauge(score: 50)),
        ),
      );

      expect(find.text('/ 100'), findsOneWidget);
    });
  });

  group('scoreColor', () {
    test('returns green for excellent score', () {
      expect(scoreColor(85), kScoreExcellent);
      expect(scoreColor(100), kScoreExcellent);
    });

    test('returns yellow for high score', () {
      expect(scoreColor(65), kScoreHigh);
      expect(scoreColor(80), kScoreHigh);
    });

    test('returns orange for medium score', () {
      expect(scoreColor(45), kScoreMedium);
      expect(scoreColor(60), kScoreMedium);
    });

    test('returns red for low score', () {
      expect(scoreColor(15), kScoreLow);
      expect(scoreColor(30), kScoreLow);
    });
  });
}
