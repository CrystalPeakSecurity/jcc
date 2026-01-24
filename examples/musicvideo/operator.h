// operator.h - Operator state for square wave generation

#ifndef OPERATOR_H
#define OPERATOR_H

static byte op_active;

void ops_init(void) { op_active = 0; }

void op_note_on(void) { op_active = 1; }

void op_note_off(void) { op_active = 0; }

#endif // OPERATOR_H
