// brainf*ck to c-lang translator
// 2018-04-24 - 2020-04-30

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <libgen.h>
#include <time.h>

static char* VERSION = "@(#) $Id: bf2c.c 0.1.2 2020-04-30 19:41 yoshi Exp $";
static char* USAGE_MESSAGE = "Usage: bf2c [options] source.bf\n"
    "Options:\n"
    "  -o, --output <file>       : output file(c-source)\n"
    "  -F, --force-flush         : force flush\n"
    "  -O, --output-default      : default param is output-file\n"
    "  -I, --inupt-default       : default param is input-file\n"
    "  -M, --message-default     : default param is message-string\n"
    "  -s, --size <number>       : array size (default:30000)\n"
    "  -1, --cell-char           : cell size is 8 bit (default)\n"
    "  -2, --cell-short          : cell size is 16 bit\n"
    "  -4, --cell-int            : cell size is 32 bit\n"
    "  -z, --eof-zero            : EOF is zero by getchar\n"
    "  -m, --eof-minus           : EOF is -1 by getchar (default)\n"
    "  -n, --eof-no-effect       : EOF is no effect by getchar\n"
    "  -C, --copyright <str>     : copyright / license message\n"
    "  -V, --verion-string <str> : version information message\n"
    "  -v, --version             : display version information\n"
    "  -h, --help                : display help information\n";

enum EOF_KIND {
    EOF_ZERO = 0,
    EOF_MINUS,
    EOF_NO_EFFECT,
};

enum DEF_PARAM {
    DEF_NONE = 0,
    DEF_OUTPUT,
    DEF_INPUT,
    DEF_MESSAGE,
};

static int array_size = 30000;
static char* cell_type = "char";
static int eof_kind = EOF_MINUS;

static char* target_version = NULL;
static char* target_copyright = NULL;

static int def_param = DEF_NONE;
static char* output_path = NULL;
static int force_flush = 0;

// options, usage message
struct option longopts[] = {
    { "help", no_argument, NULL, 'h' },
    { "version", no_argument, NULL, 'v' },
    { "output", required_argument, NULL, 'o' },
    { "size", required_argument, NULL, 's' },
    { "version-string", required_argument, NULL, 'V' },
    { "copyright", required_argument, NULL, 'C' },
    { "force-flush", no_argument, NULL, 'F' },
    { "output-default", no_argument, NULL, 'O' },
    { "input-default", no_argument, NULL, 'I' },
    { "message-default", no_argument, NULL, 'M' },
    { "cell-char", no_argument, NULL, '1' },
    { "cell-short", no_argument, NULL, '2' },
    { "cell-int", no_argument, NULL, '4' },
    { "eof-zero", no_argument, NULL, 'z' },
    { "eof-minus", no_argument, NULL, 'm' },
    { "eof-no-effect", no_argument, NULL, 'n' },
    { NULL, 0, NULL, '\0' },
};

/** duplicate string. required call free(). */
char* dup_string(char* string) {
    char* new_string = (char*) malloc(strlen(string)+1);
    strcpy(new_string, string);
    return new_string;
}

/** create version info. required call free() */
char* create_version_info(char* input_path) {
    char* input_file = dup_string(input_path);
    char* base_name = basename(input_file);
    char time_stamp[25];

    time_t now = time(NULL);
    struct tm *tmp = localtime(&now);
    if (tmp == NULL) {
        perror("localtime");
        exit(1);
    }

    if (strftime(time_stamp, sizeof(time_stamp), "%F %T%z", tmp) == 0) {
        fprintf(stderr, "error: strftime()");
        exit(1);
    }

    char* user_name = getenv("LOGNAME");
    if (user_name == NULL) {
        user_name = getenv("USER");
    }
    if (user_name == NULL) {
        user_name = getenv("LNAME");
    }
    if (user_name == NULL) {
        user_name = getenv("USERNAME");
    }
    if (user_name == NULL) {
        user_name = "noname";
    }

    char* version_info = (char*) malloc(
        strlen(base_name)
        + strlen(time_stamp)
        + strlen(user_name)
        + 40);
    sprintf(version_info, "@(%c) $%s: %s 0.1.0 %s %s Exp $",
        '#', "Id", base_name, time_stamp, user_name);

    free(input_file);
    return version_info;
}

int options(int argc, char**argv) {
    char* input_path=NULL;
    char* output_path=NULL;
    int opt,longindex;
    int show_help = 0;
    int show_version = 0;
    while((opt=getopt_long(argc, argv, "hvo:s:V:C:FOIM124zmn",
            longopts, &longindex)) != -1) {
        switch(opt) {
        case 'h': show_help |= 1; break;
        case 'v': show_version = 1; break;
        case 'o': output_path = optarg; break;
        case 's':
            array_size = atoi(optarg);
            if (array_size < 1) {
                printf("%s: invalid argument. -s or --size\n", argv[0]);
                show_help = 2;
            }
            break;
        case 'V': target_version = optarg; break;
        case 'C': target_copyright = optarg; break;
        case 'F': force_flush = 1; break;
        case 'O': def_param = DEF_OUTPUT; break;
        case 'I': def_param = DEF_INPUT; break;
        case 'M': def_param = DEF_MESSAGE; break;
        case '1': cell_type = "char"; break;
        case '2': cell_type = "short"; break;
        case '4': cell_type = "int"; break;
        case 'z': eof_kind = EOF_ZERO; break;
        case 'm': eof_kind = EOF_MINUS; break;
        case 'n': eof_kind = EOF_NO_EFFECT; break;
        default: show_help=2; break;
        }
    }

    if (show_help) {
        puts(VERSION);
        puts(USAGE_MESSAGE);
        exit(show_help==1 ? 0 : 1);
    }

    if (show_version) {
        puts(VERSION);
        exit(0);
    }

    return optind;
}

/** escape string */
void escape_string(FILE* out, char* message) {
    int i;
    for (i=0; message[i] != '\0'; i++) {
        char ch = message[i];
        if (ch == '\n') {
            fputs("\\n", out);
        } else if (ch == '\t') {
            fputs("\\t", out);
        } else if (ch == '"') {
            fputs("\\\"", out);
        } else if (ch == '\\') {
            fputs("\\\\", out);
        } else {
            fputc(ch, out);
        }
    }
}

/** transrate to c-lang */
void transrate(FILE*out, FILE* in) {
    fputs("#include <stdio.h>\n", out);
    fputs("#include <stdlib.h>\n", out);
    fputs("#include <getopt.h>\n", out);
    fputs("#include <string.h>\n", out);
    fputs("#include <unistd.h>\n", out);

    if (target_version != NULL) {
        fputs("static char* VERSION = \"", out);
        escape_string(out, target_version);
        fputs("\";", out);
    }

    if (target_copyright != NULL) {
        fputs("static char* COPYRIGHT = \"", out);
        escape_string(out, target_copyright);
        fputs("\";", out);
    }

    fputs("int getchar2();\n", out);
    fputs("int options(int argc, char**argv);\n", out);

    fputs("int main(int argc, char**argv) {\n", out);
    fputs("  int idx = options(argc, argv);\n", out);
    fputs("  int ch;\n", out);
    fprintf(out, "  %s* buff = calloc(%d, sizeof(%s));\n",
        cell_type, array_size, cell_type);
    fprintf(out, "  %s* ptr = buff;\n", cell_type);

    int enable_input = 0;
    int enable_output = 0;

    int ch;
    while ((ch = fgetc(in)) != EOF) {
        if (ch == '+') {
            fputs("  (*ptr)++;\n", out);
        } else if (ch == '-') {
            fputs("  (*ptr)--;\n", out);
        } else if (ch == '<') {
            fputs("  ptr--;\n", out);
        } else if (ch == '>') {
            fputs("  ptr++;\n", out);
        } else if (ch == ',') {
            fputs("  ch = getchar2();\n", out);
            if (eof_kind == EOF_ZERO) {
                fputs("  if (ch == EOF) ch = 0;\n", out);
            }
            if (eof_kind == EOF_NO_EFFECT) {
                fputs("  if (ch != EOF)\n", out);
            }
            fputs("  *ptr = ch;\n", out);
            enable_input = 1;
        } else if (ch == '.') {
            fputs("  putchar(*ptr);\n", out);
            if (force_flush) {
                fputs("  fflush(stdout);\n", out);
            }
            enable_output = 1;
        } else if (ch == '[') {
            fputs("  while(*ptr) {\n", out);
        } else if (ch == ']') {
            fputs("  }\n", out);
        }
    }
    fputs("  free(buff);\n", out);
    fputs("  return 0;\n", out);
    fputs("}\n", out);

    // read character from stdin or message-string
    fputs("static char* message=NULL;\n", out);
    fputs("int getchar2() {\n", out);
    fputs(" if (message == NULL) {\n", out);
    fputs("   return getchar();\n", out);
    fputs(" } else if (*message == '\\0') {\n", out);
    fputs("   return EOF;\n", out);
    fputs(" } else {\n", out);
    fputs("   return *(message++);\n", out);
    fputs(" }\n", out);
    fputs("}\n", out);

    if (!enable_input
          && (def_param == DEF_INPUT || def_param == DEF_MESSAGE)) {
        def_param = DEF_NONE;
    }
    if (!enable_output
          && def_param == DEF_OUTPUT) {
        def_param = DEF_NONE;
    }
    if (!enable_input && enable_output) {
        def_param = DEF_OUTPUT;
    }

    // options, usage message
    fputs("struct option longopts[] = {\n"
          "  { \"help\", no_argument, NULL, 'h' },\n"
          "  { \"version\", no_argument, NULL, 'v' },\n", out);
    if (enable_input) {
        fputs(
          "  { \"file\", required_argument, NULL, 'f' },\n"
          "  { \"message\", required_argument, NULL, 'm' },\n", out);
    }
    if (enable_output) {
        fputs(
          "  { \"output\", required_argument, NULL, 'o' },\n", out);
    }
    fputs("  { NULL, 0, NULL, '\\0' },\n"
          "};\n", out);

    fputs("int options(int argc, char**argv) {\n"
          "  char* input_path=NULL;\n"
          "  char* output_path=NULL;\n"
          "  int opt,longindex,show_help=0;\n"
          "  while((opt=getopt_long(argc, argv,\"hv\"", out);
    if (enable_input) {
        fputs(" \"f:m:\"", out);
    }
    if (enable_output) {
        fputs(" \"o:\"", out);
    }
    fputs(" , longopts, &longindex)) != -1) {\n"
          "    switch(opt) {\n"
          "    case 'h':\n"
          "    case 'v': show_help|=1; break;\n"
          "    case 'f': input_path=optarg; message=NULL; break;\n"
          "    case 'm': input_path=NULL; message=optarg; break;\n"
          "    case 'o': output_path=optarg; break;\n"
          "    default: show_help=2; break;\n"
          "    }\n"
          "  }\n", out);

    if (def_param == DEF_INPUT) {
        fputs("  if (optind < argc) {\n"
              "    input_path = argv[optind++];\n"
              "    message = NULL;\n"
              "  }\n", out);
    }
    if (def_param == DEF_OUTPUT) {
        fputs("  if (optind < argc)\n"
              "    output_path = argv[optind++];\n", out);
    }
    if (def_param == DEF_MESSAGE) {
        fputs("  if (optind < argc) {\n"
              "    input_path = NULL;\n"
              "    message = argv[optind++];\n"
              "  }\n", out);
    }
    fputs("  if (optind < argc) {\n"
          "    show_help = 2;\n"
          "  }\n", out);

    fputs("  if (show_help) {\n", out);
    if (target_version != NULL) {
        fputs("    puts(VERSION);\n", out);
    }

    if (target_copyright != NULL) {
        fputs("    puts(COPYRIGHT);\n", out);
    }
    // usage
    fputs("    printf(\"Usage:\\n  %s [options]\"", out);
    if (def_param == DEF_INPUT) {
        fputs("\" [ <input-file> ]\"", out);
    } else if (def_param == DEF_OUTPUT) {
        fputs("\" [ <output-file> ]\"", out);
    } else if (def_param == DEF_MESSAGE) {
        fputs("\" [ <input-message> ]\"", out);
    }
    fputs("\"\\n\", argv[0]);\n"
          "    puts(\"Options:\");\n", out);
    if (enable_input) {
        fputs(
          "    puts(\"  -f, --file <file>   : input file path.\");\n"
          "    puts(\"  -m, --message <str> : input message.\");\n", out);
    }
    if (enable_output) {
        fputs(
          "    puts(\"  -o, --output <file> : output file path.\");\n", out);
    }
    fputs("    puts(\"  -v, --version       : display version information.\");\n"
          "    puts(\"  -h, --help          : display help message.\");\n", out);
    fputs("    exit(show_help==1 ? 0 : 1);\n"
          "  }\n", out);

    fputs("  if (input_path != NULL\n"
          "      && strcmp(input_path, \"-\") != 0) {\n"
          "    FILE* in = fopen(input_path, \"r\");\n"
          "    if(in==NULL){\n"
          "      perror(\"fopen()\");\n"
          "      exit(1);\n"
          "    }\n"
          "    int rc = dup2(fileno(in), 0);\n"
          "    if(rc==-1){\n"
          "      perror(\"dup2(in)\");\n"
          "      exit(1);\n"
          "    }\n"
          "  }\n", out);

    fputs("  if (output_path != NULL\n"
          "      && strcmp(output_path, \"-\") != 0) {\n"
          "    FILE* out = fopen(output_path, \"w\");\n"
          "    int rc = dup2(fileno(out), 1);\n"
          "    if(rc==-1){\n"
          "      perror(\"dup2(out)\");\n"
          "      exit(1);\n"
          "    }\n"
          "  }\n", out);

    fputs("  return optind;\n"
          "}\n", out);
}

/** create output path(*.c) from input path(*.bf). required call free() */
char* create_output_path(char* input_path) {

    char* input_path_wk1 = dup_string(input_path);
    char* dir_path = dup_string(dirname(input_path_wk1));
    free(input_path_wk1);

    char* input_path_wk2 = dup_string(input_path);
    char* base_name = dup_string(basename(input_path_wk2));
    free(input_path_wk2);

    // remove extension
    char* pos = strrchr(base_name, '.');
    if (pos != NULL) {
        *pos = '\0';
    }

    // create output path
    char* output_path = (char*) malloc(
        strlen(dir_path)
        + 1 // size of "/"
        + strlen(base_name)
        + 3); // size of ".c\0"
    strcpy(output_path, dir_path);
    strcat(output_path, "/");
    strcat(output_path, base_name);
    strcat(output_path, ".c");

    free(dir_path);
    free(base_name);

    return output_path;
}

/** entry point */
int main(int argc, char**argv) {
    int ind = options(argc, argv);

    // open inupt file(*.bf)
    char* input_path = argv[ind];
    FILE*in = fopen(input_path, "r");
    if (in == NULL) {
        perror(input_path);
        exit(1);
    }

    // open output file(*.c)
    char* output_file;
    if (output_path == NULL) {
        output_file = create_output_path(input_path);
    } else {
        output_file = dup_string(output_path);
    }
    FILE*out = fopen(output_file, "w");
    if (out == NULL) {
        perror(output_file);
        exit(1);
    }

    if (target_version == NULL) {
        target_version = create_version_info(input_path);
    } else {
        target_version = dup_string(target_version);
    }

    // main logic
    transrate(out, in);

    // clean up
    fclose(in);
    fclose(out);
    free(output_file);
    free(target_version);
    return 0;
}
