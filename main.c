#include <stdio.h>

#define A 10
#define B(X) (X+12)

int a;

void add(int a, int b)
{
    return a+b;
}

void foo(void *ppt)
{
    print("foo\n");
}

int main(int argc, char *argv[])
{
    foo(NULL);

    return 0;
}
