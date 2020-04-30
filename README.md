# brainfuck-compiler-c

brainfuck コンパイラです。

厳密にいえば、C 言語へのトランスレータになります。

## build 方法

```shell-session
git clone https://github.com/yoshi389111/brainfuck-compiler-c.git
cd brainfuck-compiler-c
make
```

## 使用方法

brainfuck のソースを `XXXXX.bf` とした場合、以下のようにします。

```shell-session
./bf2c -o XXXXX.c XXXXX.bf
gcc -O2 -o XXXXX XXXXX.c
./XXXXX
```

また、bf2c には以下のオプションがあります。

* `-o` or `--output` : 出力ファイル(Cソース)を指定します
* `-F` or `--force-flush` : １文字ごとに強制 flush します
* `-O` or `--output-default` : 実行コマンドのデフォルト引数を出力パスとします
* `-I` or `--input-default` : 実行コマンドのデフォルト引数を入力パスとします
* `-M` or `--message-default` : 実行コマンドのデフォルト引数をメッセージとします
* `-s` or `--size` : メモリ配列の数を指定します(デフォルト 30000)
* `-1` or `--cell-chear` : メモリ配列を byte の配列とします(デフォルト)
* `-2` or `--cell-short` : メモリ配列を short の配列とします
* `-4` or `--cell-int` : メモリ配列を int の配列とします
* `-z` or `--eof-zero` : EOF を 0 とします
* `-m` or `--eof-minus` : EOF を -1 とします(デフォルト)
* `-n` or `--eof-no-effect` : EOF は読み込まないようにします
* `-C` or `--copyright` : 著作権表示、あるいはライセンス表示を指定します
* `-V` or `--version-string` : バージョン情報を指定します
* `-v` or `--version` : コンパイラのバージョンを表示します
* `-h` or `--help` : ヘルプメッセージを表示します

`-V` でバージョン情報を指定しなかった場合には、ソースファイル名、現在日付、ログイン名などをもとにデフォルトの情報を埋め込みます。ログイン名は環境変数を `LOGNAME` `USER` `LNAME` `USERNAME` の順序でチェックして、最初の空ではない文字列が設定されていたものを使います（チェックする環境変数は python の `getpass.getuser()` を参考にしています）。もし、なにも設定されていない場合には `"noname"` を使います。

## コンパイルした実行コマンドの使い方

コンパイルした実行コマンドは以下のオプションを受け付けます

* `-f` or `--file` : 入力ファイル
* `-m` or `--message` : 入力メッセージ
* `-o` or `--output` : 出力ファイル
* `-v` or `--version` : バージョン情報を表示します
* `-h` or `--help` : ヘルプメッセージを表示します

ただし、brainfuck のソースファイルに、 `,` コマンドが使われていない場合、入力ファイルおよび入力メッセージのオプションは指定できません。

同様に、 `.` コマンドが使われていない場合、出力ファイルのオプションは指定できません。

また、バージョン情報とヘルプメッセージは同じ表示になります。

入力ファイル、入力メッセージが指定されていない場合には、標準入力から読み込みます。
同様に、出力ファイルが指定されていない場合には、標準出力に書き込みます。

コンパイル時に実行コマンドのデフォルト引数を指定していた場合( `-I` or `-M` or `-O` )には、１つだけオプションなしで引数を指定可能です。

## 使用例

`cat` コマンド相当のソースをコンパイルしてみます。

```brainfuck:mycat.bf
,[.,]
```

この場合、EOF を 0 にする必要があるので以下のようにコンパイル、実行します。


```shell-session
$ ./bf2c -zIo mycat.c -C "MIT License" -V "mycat ver 0.0.0.1" mycat.bf
$ gcc -O2 -o mycat mycat.c
$ ./mycat --version
mycat ver 0.0.0.1
MIT License
Usage:
  ./mycat [options] [ <input-file> ]
Options:
  -f, --file <file>   : input file path.
  -m, --message <str> : input message.
  -o, --output <file> : output file path.
  -v, --version       : display version information.
  -h, --help          : display help message.
$ ./mycat mycat.bf
,[.,]
```

