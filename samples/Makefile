PROGRAMS=mandelbrot mandelbrot_color julia julia_color

all: $(PROGRAMS:=.bf)

clean:
	rm -f *.c *.bf $(PROGRAMS)

test:
	python3 -m mypy *.py
	python3 -m doctest *.py
	python3 -m unittest test_*.py

%.bf: %.py bf_core.py bf_stack.py
	python3 -B $< > $@

%.c: %.bf ../bf2c
	../bf2c -F $<

%: %.c
	gcc -O2 -o $@ $<

# ../bf2c:
# 	cd .. ; make

# create virtual environment
venv:
	python3 -m venv .venv

# install for development(at venv)
dev-install:
	python3 -m pip install -r requirements.txt
