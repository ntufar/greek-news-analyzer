import 'package:flutter/material.dart';

const String kApiBaseUrl = 'https://epap.vercel.app';

const Color kPrimaryDark = Color(0xFF1E3C72);
const Color kPrimaryLight = Color(0xFF2A5298);
const Color kBackgroundStart = Color(0xFFE8EDF5);
const Color kBackgroundEnd = Color(0xFFD5DCE8);
const Color kScoreExcellent = Color(0xFF28A745);
const Color kScoreHigh = Color(0xFFFFC107);
const Color kScoreMedium = Color(0xFFFD7E14);
const Color kScoreLow = Color(0xFFDC3545);

const int kMinTextLength = 50;
const int kMaxTextLength = 10000;

const List<int> kScoreThresholds = [81, 61, 31, 1];

Color scoreColor(int score) {
  if (score >= 81) return kScoreExcellent;
  if (score >= 61) return kScoreHigh;
  if (score >= 31) return kScoreMedium;
  return kScoreLow;
}

String scoreLabel(int score) {
  if (score >= 81) return 'Εξαιρετική';
  if (score >= 61) return 'Υψηλή';
  if (score >= 31) return 'Μέτρια';
  return 'Χαμηλή';
}

const List<String> kGreekNewsDomains = [
  'kathimerini.gr', 'tovima.gr', 'naftemporiki.gr', 'protothema.gr',
  'skai.gr', 'ert.gr', 'ant1.gr', 'mega.gr', 'alpha.gr',
  'news247.gr', 'in.gr', 'lifo.gr', 'efsyn.gr',
];
