// Stub para compilação web - File não disponível no web
class File {
  File(String path) {
    throw UnsupportedError('File não disponível no web');
  }
  
  Future<bool> exists() async => false;
  Future<int> length() async => 0;
  Future<List<int>> readAsBytes() async => [];
  Future<void> delete() async {}
}

