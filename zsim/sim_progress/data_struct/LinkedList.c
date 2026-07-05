#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <structmember.h>
#include <stdlib.h>
#pragma execution_character_set("utf-8")


// 节点结构定义
typedef struct Node {
    PyObject* data;  // 存储 Python 对象
    struct Node* next;
} Node;

// 链表结构定义
typedef struct {
    PyObject_HEAD
    Node* head;
    int length;
} LinkedList;

// 定义迭代器结构
typedef struct {
    PyObject_HEAD
    Node* current;
    LinkedList* list;
} LinkedListIterator;

// 迭代器的 next 方法
static PyObject* LinkedList_iternext(LinkedListIterator* iter) {
    if (iter->current == NULL) {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
    PyObject* data = iter->current->data;
    Py_INCREF(data);
    iter->current = iter->current->next;
    return data;
}


// 迭代器的析构函数
static void LinkedListIterator_dealloc(LinkedListIterator* self) {
    Py_XDECREF(self->list);
    PyObject_GC_UnTrack(self);
    PyObject_GC_Del(self);
}

// 迭代器的遍历函数
static int LinkedListIterator_traverse(LinkedListIterator *self, visitproc visit, void *arg) {
    Py_VISIT(self->list);
    return 0;
}

// 定义迭代器类型
static PyTypeObject LinkedListIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "LinkedList.LinkedListIterator",
    .tp_basicsize = sizeof(LinkedListIterator),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_iternext = (iternextfunc)LinkedList_iternext,
    .tp_dealloc = (destructor)LinkedListIterator_dealloc,
    .tp_traverse = (traverseproc)LinkedListIterator_traverse,
};

// 创建新的链表对象
static PyObject* LinkedList_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    LinkedList* self = (LinkedList*)type->tp_alloc(type, 0);
    if (self) {
        self->head = NULL;
        self->length = 0;
    }
    return (PyObject*)self;
}

// 销毁链表对象
static void LinkedList_dealloc(LinkedList* self) {
    Node* current = self->head;
    while (current) {
        Node* temp = current;
        Py_XDECREF(temp->data);
        current = current->next;
        free(temp);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

// 添加节点到尾部
static PyObject* LinkedList_add(LinkedList* self, PyObject* args) {
    PyObject* data;
    if (!PyArg_ParseTuple(args, "O", &data)) {
        return NULL;
    }
    Py_INCREF(data);

    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) {
        Py_DECREF(data);
        return PyErr_NoMemory();
    }
    new_node->data = data;
    new_node->next = NULL;

    if (!self->head) {
        self->head = new_node;
    } else {
        Node* current = self->head;
        while (current->next) {
            current = current->next;
        }
        current->next = new_node;
    }
    self->length++;

    Py_RETURN_NONE;
}

static PyObject* LinkedList_insert(LinkedList* self, PyObject* args) {
    PyObject* data;
    if (!PyArg_ParseTuple(args, "O", &data)) {
        return NULL;  // 如果参数解析失败，返回 NULL
    }

    Py_INCREF(data);  // 增加引用计数，确保数据不会被回收

    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) {
        Py_DECREF(data);
        return PyErr_NoMemory();  // 如果分配失败，返回内存错误
    }

    new_node->data = data;
    new_node->next = self->head;  // 新节点的 next 指向当前链表的头节点

    self->head = new_node;        // 更新链表头指针为新节点
    self->length++;               // 链表长度加 1

    Py_RETURN_NONE;  // 返回 None
}

static PyObject* LinkedList_pop_head(LinkedList* self, PyObject* Py_UNUSED(ignored)) {
    // 检查链表是否为空
    if (self->head == NULL) {
        Py_RETURN_NONE; // 如果链表为空，返回 None
    }
    // 保存当前头节点
    Node* old_head = self->head;
    // 获取头节点的数据
    PyObject* removed_data = old_head->data;
    // 更新头节点为下一个节点
    self->head = old_head->next;
    // 释放旧头节点内存
    free(old_head);
    // 减少链表长度
    self->length--;
    // 增加返回数据的引用计数，防止被垃圾回收
    Py_INCREF(removed_data);

    return removed_data; // 返回移除的数据
}

static PyObject* LinkedList_remove(LinkedList* self, PyObject* data) {
    if (self->head == NULL) {
        PyErr_SetString(PyExc_ValueError, "Cannot remove from empty list.");
        return NULL;
    }

    Node* current = self->head;
    Node* prev = NULL;

    while (current) {
        int comparison_result = PyObject_RichCompareBool(current->data, data, Py_EQ);
        if (comparison_result == -1) {
            // 处理比较失败的情况
            PyErr_SetString(PyExc_TypeError, "Error comparing data types.");
            return NULL;
        }
        if (comparison_result) {
            // 找到匹配项，进行删除操作
            Py_XDECREF(current->data);  // 安全地减少引用计数
            if (prev == NULL) {
                self->head = current->next;
            } else {
                prev->next = current->next;
            }
            free(current);
            Py_RETURN_TRUE;
        } else {
            prev = current;
            current = current->next;
        }
    }

    Py_RETURN_FALSE;
}

// 创建新的迭代器对象
static PyObject* LinkedList_iter(LinkedList* self) {
    LinkedListIterator* iter = (LinkedListIterator*)PyObject_GC_New(LinkedListIterator, &LinkedListIteratorType);
    if (iter == NULL) {
        return NULL;
    }
    iter->current = self->head;
    iter->list = self;
    Py_INCREF(self);
    PyObject_GC_Track(iter);
    return (PyObject*)iter;
}

static PyObject* LinkedList_getitem(LinkedList* self, Py_ssize_t index) {
    if (index < 0 || index >= self->length) {
        PyErr_SetString(PyExc_IndexError, "Index out of range.");
        return NULL;
    }

    Node* current = self->head;
    for (Py_ssize_t i = 0; i < index; i++) {
        current = current->next;
    }
    Py_INCREF(current->data);
    return current->data;
}

// 获取链表长度
static PyObject* LinkedList_length(LinkedList* self, void* closure) {
    return self->length;
}

// 链表字符串表示
static PyObject* LinkedList_str(LinkedList* self) {
    PyObject* result = PyList_New(0);
    Node* current = self->head;
    while (current) {
        PyList_Append(result, current->data);
        current = current->next;
    }
    PyObject* str_result = PyObject_Str(result);
    Py_DECREF(result);
    return str_result;
}

// 定义获取链表长度的函数
static Py_ssize_t LinkedList_sq_length(LinkedList* self) {
    return self->length;
}

static PyObject* LinkedList_gethead(LinkedList* self, void* closure) {
    if (self->head) {
        Py_INCREF(self->head->data);
        return self->head->data;
    }
    Py_RETURN_NONE;
};

static PyObject* LinkedList_getnext(LinkedList* self, void* closure) {
    if (self->head) {
        Py_INCREF(self->head->next);
        return self->head->next;
    }
    Py_RETURN_NONE;
}

static int LinkedList_is_empty(LinkedList* self) {
    return self->head == NULL;
}

static int LinkedList_bool(LinkedList* self) {
    return !LinkedList_is_empty(self);
}


// 定义链表的方法
static PyMethodDef LinkedList_methods[] = {
    {"add", (PyCFunction)LinkedList_add, METH_VARARGS, "Add an element to the linked list."},
    {"insert", (PyCFunction)LinkedList_insert, METH_VARARGS, "Insert an element to the linked list."},
    {"pop_head", (PyCFunction)LinkedList_pop_head, METH_NOARGS, "Remove and return the head element of the linked list."},
    {"remove", (PyCFunction)LinkedList_remove, METH_VARARGS, "Remove an element from the linked list."},
    {NULL}  // Sentinel
};

// 定义链表的成员
static PyGetSetDef LinkedList_getset[] = {
    {"head", (getter)LinkedList_gethead, NULL, "Get the head element of the linked list.", NULL},
    {"next", (getter)LinkedList_getnext, NULL, "Get the next element of the linked list.", NULL},
    {"length", (getter)LinkedList_length, NULL, "Get the length of the linked list.", NULL},
    {NULL}  // Sentinel
};

// 链表类型定义
static PyTypeObject LinkedListType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "LinkedList",
    .tp_doc = "A simple linked list.",
    .tp_basicsize = sizeof(LinkedList),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = LinkedList_new,
    .tp_dealloc = (destructor)LinkedList_dealloc,
    .tp_methods = LinkedList_methods,
    .tp_getset = LinkedList_getset,
    .tp_str = (reprfunc)LinkedList_str,
    .tp_iter = (getiterfunc)LinkedList_iter,
    // .tp_bool = (inquiry)LinkedList_bool,
    .tp_as_sequence = &(PySequenceMethods){
        .sq_item = (ssizeargfunc)LinkedList_getitem,
        .sq_length = (lenfunc)LinkedList_sq_length,
    },
    .tp_as_mapping = &(PyMappingMethods){
        .mp_length = (lenfunc)LinkedList_sq_length,
    },
};

// 模块初始化
static PyModuleDef LinkedListmodule = {
    PyModuleDef_HEAD_INIT,
    "LinkedList",
    "A simple linked list module.",
    -1,
};

PyMODINIT_FUNC PyInit_LinkedList(void) {
    PyObject* m;
    if (PyType_Ready(&LinkedListType) < 0) {
        return NULL;
    }
    m = PyModule_Create(&LinkedListmodule);
    if (!m) {
        return NULL;
    }
    Py_INCREF(&LinkedListType);
    PyModule_AddObject(m, "LinkedList", (PyObject*)&LinkedListType);
    return m;
}