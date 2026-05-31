const _scoreRegex = r'ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ:\s*(\d{1,3})';
const _sectionRegex = r'\*\*(\d+\.\s*[^:]+):\*\*';

class ParsedAnalysis {
  final int score;
  final String rawMarkdown;
  final Map<String, String> sections;

  ParsedAnalysis({
    required this.score,
    required this.rawMarkdown,
    required this.sections,
  });
}

int extractScore(String markdown) {
  final regex = RegExp(_scoreRegex);
  final match = regex.firstMatch(markdown);
  if (match == null) return 0;
  return int.parse(match.group(1)!);
}

ParsedAnalysis parseAnalysis(String markdown) {
  final score = extractScore(markdown);
  final sections = <String, String>{};

  final sectionRegex = RegExp(_sectionRegex);
  final matches = sectionRegex.allMatches(markdown).toList();

  for (int i = 0; i < matches.length; i++) {
    final title = matches[i].group(1)!.trim();
    final start = matches[i].end;

    final end = i + 1 < matches.length
        ? matches[i + 1].start
        : markdown.length;

    final content = markdown.substring(start, end).trim();
    sections[title] = content;
  }

  return ParsedAnalysis(
    score: score,
    rawMarkdown: markdown,
    sections: sections,
  );
}
