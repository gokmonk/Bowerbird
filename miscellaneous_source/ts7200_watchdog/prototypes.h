/* generated by /home/andrewt/bin/prototypes ts7200_watchdog.c util.c option.c */

/* ts7200_watchdog.c */

extern char *version ;
void initialize_options(void);

/* util.c */

extern char *myname;
void set_myname(char *argv[]);
void die(char *format, ...) __attribute__ ((noreturn)) ;
extern double  epsilon ;
#ifndef __GNUC__
#define __attribute__()
#endif
double approximately_zero(double x) __attribute__ ((pure)) ;
extern int		verbosity ;
extern FILE	*debug_stream;
#ifndef __GNUC__
#define __attribute__()
#endif
void dprintf(int level, char *format, ...) __attribute__ ((format (printf, 2, 3)));
#ifndef __GNUC__
#define __attribute__()
#endif
int imax(int x, int y) __attribute__ ((const)) ;
#ifndef __GNUC__
#define __attribute__()
#endif
int imin(int x, int y) __attribute__ ((const)) ;
#ifndef __GNUC__
#define __attribute__()
#endif
double min(double x, double y) __attribute__ ((const)) ;
#ifndef __GNUC__
#define __attribute__()
#endif
double max(double x, double y) __attribute__ ((const)) ;
#ifndef __GNUC__
#define __attribute__()
#endif
double square(double x) __attribute__ ((const)) ;
#ifndef __GNUC__
#define __attribute__()
#endif
void *salloc(size_t n) __attribute__ ((malloc));
#ifndef __GNUC__
#define __attribute__()
#endif
void *srealloc(void *m, size_t n) __attribute__ ((malloc));
#ifndef __GNUC__
#define __attribute__()
#endif
char *sstrdup(char *s) __attribute__ ((malloc));
#ifndef __GNUC__
#define __attribute__()
#endif
void *sdup(void *old, size_t n) __attribute__ ((malloc));
long lcm(long x,long y);
#ifndef __GNUC__
#define __attribute__()
#endif
long gcd (long x,long y) __attribute__ ((const)) ;
void qsort_double(double *sequence, int length);
double **qsort_indices(double **indices, int length);
double **quicksort_double_indices(double *sequence, int length);
void doubles_max_min(int n, double *d, double *minimum, double *maximum);
#ifndef __GNUC__
#define __attribute__()
#endif
double exp10(double x) __attribute__ ((const)) ;
#ifndef __GNUC__
#define __attribute__()
#endif
double round10(double x, int delta) __attribute__ ((const)) ;
double entropy_i(int *x, int n);

/* option.c */

int hash(char *s);
void set_option(char *name, char *value);
void set_option_double(char *name, double d);
void set_option_int(char *name, int i);
void set_option_boolean(char *name, int i);
char *get_option(char *name);
int defined_option(char *name);
double get_option_double(char *name);
int get_option_int(char *name);
int get_option_boolean(char *name);
int get_option_keyword(char *name, char **keyword_table);
void parse_option_assignment(char *assignment);
int lookup_keyword(char *w, char **keyword_table);
