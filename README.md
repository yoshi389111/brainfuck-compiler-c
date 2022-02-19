# brainfuck-compiler-c

This program is a brainfuck compiler.

To be more precise, it is a translator to the C language.

* wikipedia: [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck)

## How to build

```shell-session
git clone https://github.com/yoshi389111/brainfuck-compiler-c.git
cd brainfuck-compiler-c
make
```

## How to use

If you set the source of brainfuck as `XXXXX.bf`, you can do the following

```shell-session
./bf2c -o XXXXX.c XXXXX.bf
gcc -O2 -o XXXXX XXXXX.c
./XXXXX
```

The following options are also available for `bf2c`.

* `-o` or `--output` `<file>`        : output file(C-source)
* `-F` or `--force-flush`            : force flush
* `-O` or `--output-default`         : default param is output-file
* `-I` or `--input-default`          : default param is input-file
* `-M` or `--message-default`        : default param is message-string
* `-s` or `--size` `<number>`        : array size (default:30000)
* `-1` or `--cell-chear`             : cell size is char of C-Lang (default)
* `-2` or `--cell-short`             : cell size is short of C-Lang (default)
* `-4` or `--cell-int`               : cell size is int of C-Lang (default)
* `-z` or `--eof-zero`               : EOF is zero by getchar
* `-m` or `--eof-minus`              : EOF is -1 by getchar (default)
* `-n` or `--eof-no-effect`          : EOF is no effect by getchar
* `-C` or `--copyright` `<str>`      : copyright / license message
* `-V` or `--version-string` `<str>` : version information message
* `-v` or `--version`                : displays version information
* `-h` or `--help`                   : displays help information

If you do not specify the version information with `-V`, it will embed the default information based on the source file name, current date, and login name.
For the login name, we check the environment variables in the order `LOGNAME` `USER` `LNAME` `USERNAME` and use the first non-empty string set (the environment variables to check are based on python's `getpass.getuser()`).
If nothing is set, use `"noname"`.

##  How to use the compiled execution command

The compiled executable command accepts the following options.

* `-f` or `--file` `<file>`   : input file path.
* `-m` or `--message` `<str>` : input message.
* `-o` or `--output` `<file>` : output file path.
* `-v` or `--version`         : displays version information.
* `-h` or `--help`            : displays help information.
* `-s` or `--size` `<number>` : array size (defaults to compile-time specification)

However, if the `,` command is not used in the source file of brainfuck, the input file and input message options cannot be specified.

Similarly, if the `.` command is not used, no options for the output file can be specified.

Also, the version information and help messages will be displayed the same.

If no input file or input message is specified, it reads from STDIN.
Similarly, if no output file is specified, it writes to the STDOUT.

If the default argument for the execution command was specified at compile time (`-I` or `-M` or `-O`), only one argument can be specified without options.

## Example of use

Try to compile the source equivalent of the `cat` command.

```brainfuck:mycat.bf
,[.,]
```

In this case, EOF needs to be set to 0, so compile and run as follows.


```shell-session
$ ./bf2c -zIo mycat.c -C "MIT License" -V "mycat ver 1.0.0" mycat.bf
$ gcc -O2 -o mycat mycat.c
$ ./mycat --version
mycat ver 1.0.0
MIT License
Usage:
  ./mycat [options] [ <input-file> ]
Options:
  -f, --file <file>   : input file path.
  -m, --message <str> : input message.
  -o, --output <file> : output file path.
  -v, --version       : display version information.
  -h, --help          : display help message.
  -s, --size <number> : array size (default:30000)
$ ./mycat mycat.bf
,[.,]
```

