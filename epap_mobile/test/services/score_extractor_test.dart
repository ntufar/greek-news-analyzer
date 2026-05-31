import 'package:flutter_test/flutter_test.dart';
import 'package:epap_mobile/utils/score_extractor.dart';

void main() {
  group('extractScore', () {
    test('extracts score from typical analysis response', () {
      final markdown = '''
**ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ: 42**

**1. ΣΥΝΑΙΣΘΗΜΑΤΙΚΗ ΧΕΙΡΑΓΩΓΗΣΗ:**
- Some content
''';
      expect(extractScore(markdown), 42);
    });

    test('extracts score 100', () {
      final markdown = '**ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ: 100**';
      expect(extractScore(markdown), 100);
    });

    test('extracts score 1', () {
      final markdown = '**ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ: 1**';
      expect(extractScore(markdown), 1);
    });

    test('returns 0 when no score found', () {
      final markdown = 'No score in this text';
      expect(extractScore(markdown), 0);
    });

    test('returns 0 for empty string', () {
      expect(extractScore(''), 0);
    });
  });

  group('parseAnalysis', () {
    test('parses all 7 sections from valid markdown', () {
      final markdown = '''
**ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ: 75**

**1. ΣΥΝΑΙΣΘΗΜΑΤΙΚΗ ΧΕΙΡΑΓΩΓΗΣΗ:**
- Χρήση φορτωμένων λέξεων
- Συναισθηματικές εκφράσεις

**2. ΔΕΙΚΤΕΣ ΠΡΟΚΑΤΑΛΗΨΗΣ:**
- Πολιτική κλίση

**3. ΑΝΑΛΟΓΙΑ ΓΕΓΟΝΟΤΩΝ vs ΓΝΩΜΕΣ:**
- 60% γεγονότα, 40% γνώμες

**4. ΑΞΙΟΠΙΣΤΙΑ ΠΗΓΗΣ:**
- Αξιόπιστη πηγή

**5. ΓΛΩΣΣΙΚΗ ΑΝΑΛΥΣΗ:**
- Ουδέτερο λεξιλόγιο

**6. ΛΟΓΙΚΕΣ ΠΛΑΝΕΣ:**
- Καμία λογική πλάνη

**7. ΣΥΣΤΑΣΗ:**
- Περαιτέρω έλεγχος
''';

      final parsed = parseAnalysis(markdown);
      expect(parsed.score, 75);
      expect(parsed.sections.length, 7);
      expect(parsed.sections.containsKey('1. ΣΥΝΑΙΣΘΗΜΑΤΙΚΗ ΧΕΙΡΑΓΩΓΗΣΗ'), true);
      expect(parsed.sections.containsKey('7. ΣΥΣΤΑΣΗ'), true);
      expect(parsed.rawMarkdown, markdown);
    });

    test('handles markdown with missing sections', () {
      final markdown = '''
**ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ: 30**

**1. ΣΥΝΑΙΣΘΗΜΑΤΙΚΗ ΧΕΙΡΑΓΩΓΗΣΗ:**
- Some text
''';

      final parsed = parseAnalysis(markdown);
      expect(parsed.score, 30);
      expect(parsed.sections.length, 1);
    });

    test('handles empty markdown', () {
      final parsed = parseAnalysis('');
      expect(parsed.score, 0);
      expect(parsed.sections.isEmpty, true);
    });
  });
}
