#ifndef ACTIONSTACK_H
#define ACTIONSTACK_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <vector>
#include <stdexcept>

// 定义 ActionStack 类
class ActionStack {
public:
    ActionStack() {}

    ~ActionStack() {
        for (PyObject* item : stack) {
            Py_DECREF(item);
        }
    }

    void push(PyObject* item) {
        Py_INCREF(item);
        stack.push_back(item);
        if (stack.size() > 2) {
            Py_DECREF(stack.front());
            stack.erase(stack.begin());
        }
    }

    PyObject* pop() {
        if (is_empty()) {
            throw std::out_of_range("Stack is empty");
        }
        PyObject* item = stack.back();
        stack.pop_back();
        return item;
    }

    PyObject* peek() const {
        if (is_empty()) {
            throw std::out_of_range("Stack is empty");
        }
        return stack.back();
    }

    bool is_empty() const {
        return stack.empty();
    }

    PyObject* peek_bottom() const {
        if (is_empty()) {
            throw std::out_of_range("Stack is empty");
        }
        return stack.front();
    }

    size_t size() const {
        return stack.size();
    }

    std::string to_string() const {
        std::string result = "[";
        for (size_t i = 0; i < stack.size(); ++i) {
            PyObject* item = stack[i];
            PyObject* str = PyObject_Str(item);
            if (str == NULL) {
                return "Error converting to string";
            }
            result += PyUnicode_AsUTF8(str);
            Py_DECREF(str);
            if (i < stack.size() - 1) {
                result += ", ";
            }
        }
        result += "]";
        return result;
    }

    PyObject* operator[](size_t index) const {
        if (index >= stack.size()) {
            throw std::out_of_range("Index out of range");
        }
        return stack[index];
    }

    bool operator==(const ActionStack& other) const {
        if (stack.size() != other.stack.size()) {
            return false;
        }
        for (size_t i = 0; i < stack.size(); ++i) {
            if (stack[i] != other.stack[i]) {
                return false;
            }
        }
        return true;
    }

    bool operator!=(const ActionStack& other) const {
        return !(*this == other);
    }

    // 迭代器类
    class ActionStackIterator {
    public:
        ActionStackIterator(ActionStack* stack) : stack_(stack), index_(0) {}

        PyObject* next() {
            if (index_ >= stack_->size()) {
                PyErr_SetString(PyExc_StopIteration, "No more items");
                return NULL;
            }
            PyObject* item = stack_->operator[](index_);
            Py_INCREF(item);
            index_++;
            return item;
        }

    private:
        ActionStack* stack_;
        size_t index_;
    };

private:
    std::vector<PyObject*> stack;
};

// 定义 ActionStack 对象类型
typedef struct {
    PyObject_HEAD
    ActionStack* action_stack;
} PyActionStack;

// 定义 ActionStack 迭代器对象类型
typedef struct {
    PyObject_HEAD
    ActionStack::ActionStackIterator* iterator;
} PyActionStackIterator;

// 方法声明
static int PyActionStack_init(PyActionStack* self, PyObject* args, PyObject* kwargs);
static void PyActionStack_dealloc(PyActionStack* self);
static int PyActionStackIterator_init(PyActionStackIterator* self, PyObject* args, PyObject* kwargs);
static void PyActionStackIterator_dealloc(PyActionStackIterator* self);
static PyObject* PyActionStack_push(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_pop(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_peek(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_is_empty(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_peek_bottom(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_size(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_to_string(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_getitem(PyActionStack* self, PyObject* args);
static PyObject* PyActionStack_eq(PyActionStack* self, PyObject* other);
static PyObject* PyActionStack_ne(PyActionStack* self, PyObject* other);
static PyObject* PyActionStack_iter(PyActionStack* self);
static PyObject* PyActionStackIterator_next(PyActionStackIterator* self);

// 方法定义
static PyMethodDef PyActionStack_methods[] = {
    {"push", (PyCFunction)PyActionStack_push, METH_VARARGS, "Push an item onto the stack."},
    {"pop", (PyCFunction)PyActionStack_pop, METH_NOARGS, "Pop an item from the stack."},
    {"peek", (PyCFunction)PyActionStack_peek, METH_NOARGS, "Peek at the top item of the stack."},
    {"is_empty", (PyCFunction)PyActionStack_is_empty, METH_NOARGS, "Check if the stack is empty."},
    {"peek_bottom", (PyCFunction)PyActionStack_peek_bottom, METH_NOARGS, "Peek at the bottom item of the stack."},
    {"size", (PyCFunction)PyActionStack_size, METH_NOARGS, "Get the size of the stack."},
    {"to_string", (PyCFunction)PyActionStack_to_string, METH_NOARGS, "Get the string representation of the stack."},
    {"__getitem__", (PyCFunction)PyActionStack_getitem, METH_VARARGS, "Get item by index."},
    {"__eq__", (PyCFunction)PyActionStack_eq, METH_O, "Check equality with another ActionStack."},
    {"__ne__", (PyCFunction)PyActionStack_ne, METH_O, "Check inequality with another ActionStack."},
    {"__iter__", (PyCFunction)PyActionStack_iter, METH_NOARGS, "Return an iterator object."},
    {NULL}  // Sentinel
};

// 迭代器方法定义
static PyMethodDef PyActionStackIterator_methods[] = {
    {"__next__", (PyCFunction)PyActionStackIterator_next, METH_NOARGS, "Return the next item from the iterator."},
    {NULL}  // Sentinel
};

// 类型定义
extern PyTypeObject PyActionStackType;
extern PyTypeObject PyActionStackIteratorType;

#endif // ACTIONSTACK_H