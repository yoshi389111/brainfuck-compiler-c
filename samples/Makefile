
all: mandelbrot
	time ./mandelbrot

mandelbrot: mandelbrot.c
	gcc -O2 -o mandelbrot mandelbrot.c

julia: julia.c
	gcc -O2 -o julia julia.c

test:
	python3 -m mypy *.py
	python3 -m doctest *.py
	python3 -m unittest test_*.py

clean:
	rm -f *.c *.bf

%.bf: %.py bf_core.py bf_stack.py
	python3 -B $< > $@

%.c: %.bf ../bf2c
	../bf2c -F $<

../bf2c:
	cd .. ; make
