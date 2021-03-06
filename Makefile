
all: bf2c test

clean:
	rm -f bf2c my_number_validator my_number_validator.c

bf2c: bf2c.c
	gcc -O2 -o bf2c bf2c.c

test: my_number_validator
	bash -c '[ "true" == "$$(./my_number_validator 123456789018)" ]'
	bash -c '[ "false" == "$$(./my_number_validator 123456789017)" ]'

my_number_validator: my_number_validator.c
	gcc -O2 -o my_number_validator my_number_validator.c

my_number_validator.c: my_number_validator.bf bf2c
	./bf2c -M -o my_number_validator.c my_number_validator.bf
