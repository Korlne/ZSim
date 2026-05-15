#include "ActionStack.h"

// 构造函数
static int PyActionStack_init(PyActionStack* self, PyObject* args, PyObject* kwargs) {
    self->action_stack = new ActionStack();
    return 0;
}

// 析构函数
static void PyActionStack_dealloc(PyActionStack* self) {
    delete self->action_stack;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

// 迭代器构造函数
static int PyActionStackIterator_init(PyActionStackIterator* self, PyObject* args, PyObject* kwargs) {
    PyObject* action_stack_obj;
    if (!PyArg_ParseTuple(args, "O!", &PyActionStackType, &action_stack_obj)) {
        return -1;
    }
    self->iterator = new ActionStack::ActionStackIterator(((PyActionStack*)action_stack_obj)->action_stack);
    return 0;
}

// 迭代器析构函数
static void PyActionStackIterator_dealloc(PyActionStackIterator* self) {
    delete self->iterator;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

// push 方法
static PyObject* PyActionStack_push(PyActionStack* self, PyObject* args) {
    PyObject* item;
    if (!PyArg_ParseTuple(args, "O", &item)) {
        return NULL;
    }
    self->action_stack->push(item);
    Py_RETURN_NONE;
}

// pop 方法
static PyObject* PyActionStack_pop(PyActionStack* self, PyObject* args) {
    try {
        PyObject* result = self->action_stack->pop();
        Py_INCREF(result);
        return result;
    } catch (const std::out_of_range& e) {
        PyErr_SetString(PyExc_IndexError, e.what());
        return NULL;
    }
}

// peek 方法
static PyObject* PyActionStack_peek(PyActionStack* self, PyObject* args) {
    try {
        PyObject* result = self->action_stack->peek();
        Py_INCREF(result);
        return result;
    } catch (const std::out_of_range& e) {
        PyErr_SetString(PyExc_IndexError, e.what());
        return NULL;
    }
}

// is_empty 方法
static PyObject* PyActionStack_is_empty(PyActionStack* self, PyObject* args) {
    return Py_BuildValue("b", self->action_stack->is_empty());
}

// peek_bottom 方法
static PyObject* PyActionStack_peek_bottom(PyActionStack* self, PyObject* args) {
    try {
        PyObject* result = self->action_stack->peek_bottom();
        Py_INCREF(result);
        return result;
    } catch (const std::out_of_range& e) {
        PyErr_SetString(PyExc_IndexError, e.what());
        return NULL;
    }
}

// size 方法
static PyObject* PyActionStack_size(PyActionStack* self, PyObject* args) {
    return Py_BuildValue("n", self->action_stack->size());
}

// to_string 方法
static PyObject* PyActionStack_to_string(PyActionStack* self, PyObject* args) {
    std::string result = self->action_stack->to_string();
    return Py_BuildValue("s", result.c_str());
}

// __getitem__ 方法
static PyObject* PyActionStack_getitem(PyActionStack* self, PyObject* args) {
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index)) {
        return NULL;
    }
    try {
        PyObject* result = self->action_stack->operator[](index);
        Py_INCREF(result);
        return result;
    } catch (const std::out_of_range& e) {
        PyErr_SetString(PyExc_IndexError, e.what());
        return NULL;
    }
}

// __eq__ 方法
static PyObject* PyActionStack_eq(PyActionStack* self, PyObject* other) {
    if (!PyObject_TypeCheck(other, &PyActionStackType)) {
        Py_RETURN_FALSE;
    }
    PyActionStack* other_stack = (PyActionStack*)other;
    return Py_BuildValue("b", *self->action_stack == *other_stack->action_stack);
}

// __ne__ 方法
static PyObject* PyActionStack_ne(PyActionStack* self, PyObject* other) {
    if (!PyObject_TypeCheck(other, &PyActionStackType)) {
        Py_RETURN_TRUE;
    }
    PyActionStack* other_stack = (PyActionStack*)other;
    return Py_BuildValue("b", *self->action_stack != *other_stack->action_stack);
}

// __iter__ 方法
static PyObject* PyActionStack_iter(PyActionStack* self) {
    PyActionStackIterator* iterator = (PyActionStackIterator*)PyObject_New(PyActionStackIterator, &PyActionStackIteratorType);
    if (iterator == NULL) {
        return NULL;
    }
    if (PyActionStackIterator_init(iterator, (PyObject*)self, NULL) < 0) {
        Py_DECREF(iterator);
        return NULL;
    }
    return (PyObject*)iterator;
}

// 迭代器 __next__ 方法
static PyObject* PyActionStackIterator_next(PyActionStackIterator* self) {
    return self->iterator->next();
}

// 类型定义
PyTypeObject PyActionStackType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ActionStack.ActionStack",                  // tp_name
    sizeof(PyActionStack),                      // tp_basicsize
    0,                                          // tp_itemsize
    (destructor)PyActionStack_dealloc,          // tp_dealloc
    0,                                          // tp_print
    0,                                          // tp_getattr
    0,                                          // tp_setattr
    0,                                          // tp_reserved
    0,                                          // tp_repr
    0,                                          // tp_as_number
    0,                                          // tp_as_sequence
    0,                                          // tp_as_mapping
    0,                                          // tp_hash
    0,                                          // tp_call
    0,                                          // tp_str
    0,                                          // tp_getattro
    0,                                          // tp_setattro
    0,                                          // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                         // tp_flags
    "A simple action stack.",                   // tp_doc
    0,                                          // tp_traverse
    0,                                          // tp_clear
    0,                                          // tp_richcompare
    0,                                          // tp_weaklistoffset
    0,                                          // tp_iter
    0,                                          // tp_iternext
    PyActionStack_methods,                      // tp_methods
    0,                                          // tp_members
    0,                                          // tp_getset
    0,                                          // tp_base
    0,                                          // tp_dict
    0,                                          // tp_descr_get
    0,                                          // tp_descr_set
    0,                                          // tp_dictoffset
    (initproc)PyActionStack_init,               // tp_init
    0,                                          // tp_alloc
    PyType_GenericNew,                          // tp_new
};

// 迭代器类型定义
PyTypeObject PyActionStackIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ActionStack.ActionStackIterator",          // tp_name
    sizeof(PyActionStackIterator),              // tp_basicsize
    0,                                          // tp_itemsize
    (destructor)PyActionStackIterator_dealloc,  // tp_dealloc
    0,                                          // tp_print
    0,                                          // tp_getattr
    0,                                          // tp_setattr
    0,                                          // tp_reserved
    0,                                          // tp_repr
    0,                                          // tp_as_number
    0,                                          // tp_as_sequence
    0,                                          // tp_as_mapping
    0,                                          // tp_hash
    0,                                          // tp_call
    0,                                          // tp_str
    0,                                          // tp_getattro
    0,                                          // tp_setattro
    0,                                          // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                         // tp_flags
    "ActionStack iterator object",              // tp_doc
    0,                                          // tp_traverse
    0,                                          // tp_clear
    0,                                          // tp_richcompare
    0,                                          // tp_weaklistoffset
    PyObject_SelfIter,                          // tp_iter
    (iternextfunc)PyActionStackIterator_next,   // tp_iternext
    PyActionStackIterator_methods,              // tp_methods
    0,                                          // tp_members
    0,                                          // tp_getset
    0,                                          // tp_base
    0,                                          // tp_dict
    0,                                          // tp_descr_get
    0,                                          // tp_descr_set
    0,                                          // tp_dictoffset
    (initproc)PyActionStackIterator_init,       // tp_init
    0,                                          // tp_alloc
    PyType_GenericNew,                          // tp_new
};

// 模块初始化
static PyModuleDef ActionStackModule = {
    PyModuleDef_HEAD_INIT,
    "ActionStack",
    "A simple action stack module.",
    -1,
    NULL, NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit_ActionStack(void) {
    PyObject* m;
    if (PyType_Ready(&PyActionStackType) < 0) {
        return NULL;
    }
    if (PyType_Ready(&PyActionStackIteratorType) < 0) {
        return NULL;
    }
    m = PyModule_Create(&ActionStackModule);
    if (m == NULL) {
        return NULL;
    }
    Py_INCREF(&PyActionStackType);
    if (PyModule_AddObject(m, "ActionStack", (PyObject*)&PyActionStackType) < 0) {
        Py_DECREF(&PyActionStackType);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}