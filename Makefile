
all: bf2c test

clean:
	rm bf2c my_number_validator my_number_validator.c

bf2c: bf2c.c
	gcc -O2 -o bf2c bf2c.c

test: my_number_validator
	[ "true" == "$$(./my_number_validator 123456789018)" ]
	[ "false" == "$$(./my_number_validator 123456789017)" ]

my_number_validator: my_number_validator.c
	gcc -O2 -o my_number_validator my_number_validator.c

my_number_validator.c: my_number_validator.bf bf2c
	./bf2c -M -o my_number_validator.c my_number_validator.bf
