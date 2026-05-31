import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/analysis_result.dart';

class DatabaseService {
  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'epap_history.db');

    return openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL,
            analysis TEXT NOT NULL,
            textLength INTEGER NOT NULL,
            source TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL
          )
        ''');
      },
    );
  }

  Future<int> saveResult(AnalysisResult result) async {
    final db = await database;
    return db.insert('history', result.toMap());
  }

  Future<List<AnalysisResult>> getHistory() async {
    final db = await database;
    final maps = await db.query(
      'history',
      orderBy: 'timestamp DESC',
    );
    return maps.map((map) => AnalysisResult.fromMap(map)).toList();
  }

  Future<int> deleteResult(int id) async {
    final db = await database;
    return db.delete('history', where: 'id = ?', whereArgs: [id]);
  }

  Future<void> clearHistory() async {
    final db = await database;
    await db.delete('history');
  }

  Future<void> close() async {
    final db = await database;
    db.close();
  }
}
