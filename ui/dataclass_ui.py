"""
# Dataclass UI

A Python class that enables dataclass instance
construction from a UI.

Meant to be used for Python modules to be run
by people who don't know how to use the command line,
also known as nearly everyone who exists.

## Usage

Have any [dataclass](https://docs.python.org/3/library/dataclasses.html)
inherit from ``DataclassUI``, and it will have this class method called
``get_instance_from_ui``, which launches up a UI window for users to
fill out the class and returns the class instance that should be
consistent with what the user filled out. Read below for more information.

If you know dataclasses well, then all you need to do is populate
a dataclasses fields like you always would and the UI
will auto-generate based on your definitions.

Example:

```python
from dataclasses import dataclass
from dataclass_ui import DataclassUI
from pathlib import Path
from typing import Literal


@dataclass
class Foo(DataclassUI):
    a: int  # users must enter an integer, enforced in UI
    b: float  # users must enter a float, enforced in UI
    c: str
    d: bool  # checkbox
    e: Path  # path to file

    # dropdowns
    f1: Literal["Option 1", "Option 2", "Option 3"]
    f2: Literal[1, 2, 3]
    f3: Literal[4.2, 4.3, 4.4]

    # lists
    g: list[str]
    h: list[int]  # users must enter a list of ints, enforced in UI
    i: list[float]  # users must enter a list of floats, enforced in UI
```

These are the field types that are supported i.e.
you may only have these type annotations:

- `int, float, str, bool, Path, list[str], list[int], list[float]`
- `Literal[ <of str, int, or float> ]`

**DO NOT USE UNIONS OR OPTIONALS**. If you need to really make a value optional, consider adding a boolean value that lets a user signal that it is not in use.

`list` is interpreted as `list[str]`

With this class defined, in your code, you can call

```
foo = Foo.get_instance_from_ui()
```

and if this function returns then foo will (hopefully) always be
a valid Foo instance with all of its fields specified
populated

`get_instance_from_ui` has arguments, all optional and in this order:

- `title` (str): what title to give the window
- `desc` (str): what description to show on the top of the UI
- `custom_check` (None | `(T -> str | None)`): if specified,
  function that takes in an instance of that class and
  returns a string being the error message to show to
  the user if the instance is invalid, or None if it is
  valid (yes, it feels a bit weird).
  If this isn't specified, then this check is not
  invoked. Use this if you need to stop the user
  from being dumb. For example, ensuring that
  all path to files aren't unspecified (`str(path) != '.'`).

If you need more customization, you can assign dataclass fields
actual field instances and add metadata to them. Some metadata
will impact UI behavior. You can add metadata to a field by doing
this (all imports are either from ``typing`` or ``dataclasses``):

```python
from dataclasses import dataclass, field
from dataclass_ui import DataclassUI
from pathlib import Path


@dataclass
class Bar(DataclassUI):
    some_numeric: int = field(default=4,
                              metadata={'title':
                                            'Put some numerical\nvalue here'})
    path_to_file: Path = field(default=Path(''),
                               metadata={
                                   'filetypes': [('text files', '*.txt')]
                               })
    lst: list[str] = field(default_factory=lambda: ['among', 'us'])
```

For list default values, always use `default_factory`
since mutable values can't be used as default values.

Specifically, here's the structure for the ``metadata`` dictionary:

- `dir` (bool): for ``Path`` only, if True then this prompts the
  user to select a directory instead of a file
- `filetypes` (list[(desc, '*.extension')]): for ``Path`` only,
  have the file opener only prompt the user to select
  files of certain extensions. The format is
  `[(description of the extension, "*.extension"), ]` and this list
  may have multiple items
- `save` (bool): If True, then this file is rather a prompt to save
  a file and a "save" dialog will pop up instead of a file open
  dialog. If this is True, ``dir`` is ignored, but `filetypes` will still be used.
- `defaultextension` (str): File extension (WITH THE LEADING DOT), such as `.txt`
  that the user will see when the save dialog pops up. This is only
  applicable when `save == True`
- `title` (str): In the UI, this shows in place of the field name. Can have newlines
"""

from dataclasses import dataclass, fields, MISSING, is_dataclass
from pathlib import Path
from typing import (Literal, get_type_hints, Callable, Any,
                    get_args, get_origin, Optional, TypedDict, Iterable, TypeVar,
                    Union, Type)
import tkinter as tk
from tkinter import filedialog
from types import MappingProxyType


class _EditableListbox(tk.Listbox):
    """A listbox where you can directly edit an item via double-click
    https://stackoverflow.com/questions/64609658/python-tkinter-listbox-text-edit-in-gui
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.edit_item = None
        self.bind("<Double-1>", self._start_edit)
        self.bind('<Delete>', self.delete_selected)

    def delete_selected(self, _event) -> None:
        selected_index = self.curselection()
        if selected_index:
            for si in sorted(selected_index, reverse=True):
                self.delete(si)

    def _start_edit(self, event):
        index = self.index(f"@{event.x},{event.y}")
        self.start_edit(index)
        return "break"

    def start_edit(self, index) -> None:
        self.edit_item = index
        text = self.get(index)
        bbi = self.bbox(index)
        if bbi is None:
            # "No bounding box!!!")
            return
        y0 = bbi[1]
        entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
        entry.bind("<Return>", self.accept_edit)
        entry.bind("<Escape>", self.cancel_edit)
        entry.bind("<Double-1>", self.accept_edit)

        entry.insert(0, text)
        entry.selection_from(0)
        entry.selection_to("end")
        entry.place(relx=0, y=y0, relwidth=1, width=-1)
        entry.focus_set()
        entry.grab_set()

    def cancel_edit(self, event) -> None:
        event.widget.destroy()

    def accept_edit(self, event) -> None:
        new_data = event.widget.get()
        self.delete(self.edit_item)
        self.insert(self.edit_item, new_data)
        event.widget.destroy()


def _get_path_basename(p: str) -> str:
    if p == "":
        return "Select File"

    p = p.replace("\\", "/")
    p2 = p.split("/")
    return p2[-1]


def _validate_decimal(P: str, label: tk.Label) -> bool:
    if P == "":
        label.config(bg="white")
        return True
    try:
        float(P)
        label.config(bg="white")
        return True
    except ValueError:
        label.config(bg="red")
        return False


def _validate_integer(P: str, label: tk.Label) -> bool:
    if P == "":
        label.config(bg="white")
        return True
    try:
        int(P)
        label.config(bg="white")
        return True
    except ValueError:
        label.config(bg="red")
        return False


def _select_file(sv: tk.StringVar, title: str = "", metadata: Optional[MappingProxyType[str, Any]] = None) -> None:
    if metadata is None:
        metadata = {}
    if metadata.get("save", False):
        file_path = (filedialog.asksaveasfilename(
            title=f"Select {title}".strip(),
            defaultextension=metadata.get("defaultextension", None),
            filetypes=metadata.get("filetypes", None)
        ) if "filetypes" in metadata else filedialog.asksaveasfilename(
            title=f"Save {title}".strip(),
            defaultextension=metadata.get("defaultextension", None)))
        if file_path:
            sv.set(file_path)
    else:
        ask_directory = metadata.get("dir", False)
        file_path = (filedialog.askopenfilename(
            title=f"Select {title}".strip(),
            filetypes=metadata.get("filetypes")
        ) if "filetypes" in metadata else filedialog.askopenfilename(
            title=f"Select {title}".strip())) if not ask_directory else filedialog.askdirectory(
            title=f"Select {title}")
        if file_path:
            sv.set(file_path)


class FieldMetadata(TypedDict):
    dir: bool  # for Path, whether to select a directory instead of a file
    filetypes: Iterable[tuple[str, Union[str, list[str], tuple[str, ...]]]]  # tkinter filetypes,
    # in the format [("desc", "*.ext")]
    save: bool  # for Path, if this is True then always ask to save to a file name (always, regardless of dir)
    defaultextension: str  # ex: .txt, for save only
    title: str  # this shows in place of the py name if defined


_T = TypeVar("_T", bound="DataclassUI")


@dataclass
class DataclassUI:
    """
    Dataclass UI constructor.

    T = list, float, str (no unions)

    # ALLOWED FIELD TYPES

    Literal[T, ...]
    bool
    T
    Path
    list[T] (no unions)

    # DATACLASS FIELD METADATA f = field(metadata={...:...})

    See FieldMetadata

    "title" replaces field name with that
    """

    @classmethod
    def get_instance_from_ui(cls: Type[_T], title: str = "Form", desc: str = "",
                             custom_check: Optional[Callable[[_T], Optional[str]]] = None) -> _T:
        """Displays a UI to the user that lets them construct the dataclass.
        Return dataclass generated, or None if user input is malformed

        Custom check: function that takes in the output instance.
        Returns None if it is good to go else returns a string representing error message
        """

        if not is_dataclass(cls):
            raise ValueError("This method may only be called in dataclasses.")
        button_pushed = []
        root = tk.Tk()
        dc_fields = fields(cls)
        # print(dc_fields)
        type_hints = get_type_hints(cls)
        # print(type_hints)
        widgets: dict[str, Callable[[], Any]] = {}
        root.minsize(300, 300)
        root.title(title)
        frame = tk.Frame(root)
        frame.pack(expand=True, side="top", anchor="n")
        pdx = 5
        pdy = 5
        top_offset = 0
        if desc != "":
            top_offset += 1
            label_in = tk.Label(frame, text=desc)
            label_in.grid(row=0, column=0, columnspan=2, padx=pdx, pady=pdy)
        for i, fld in enumerate(dc_fields):
            ci = i + top_offset
            type_of = type_hints[fld.name]
            default_value = fld.default_factory() if fld.default_factory is not MISSING else fld.default
            has_default = (fld.default is not MISSING) or (fld.default_factory is not MISSING)
            # print(default_value, has_default)
            # print(type_of)

            f_name = (dict(fld.metadata) or {}).get("title", "") or fld.name
            metadata = MappingProxyType(dict(fld.metadata) or {})
            label = tk.Label(frame, text=f_name)
            if type_of == str or type_of == int or type_of == float:

                label.grid(row=ci, column=0, padx=pdx, pady=pdy, sticky='E')
                if type_of == str:
                    entry = tk.Entry(frame)
                    widgets[fld.name] = lambda e=entry: e.get()
                elif type_of == int:
                    vcmd_integer = (root.register(lambda P, lb_=label: _validate_integer(P, lb_)), '%P')
                    entry = tk.Entry(frame, validate="key", validatecommand=vcmd_integer)
                    widgets[fld.name] = lambda e=entry: int(e.get())
                else:
                    vcmd_floating = (root.register(lambda P, lb_=label: _validate_decimal(P, lb_)), '%P')
                    entry = tk.Entry(frame, validate="key", validatecommand=vcmd_floating)
                    widgets[fld.name] = lambda e=entry: float(e.get())
                entry.grid(row=ci, column=1, pady=pdy)
                if has_default:
                    entry.delete(0, tk.END)
                    entry.insert(0, default_value)
            elif type_of == bool:
                checkbox_var = tk.BooleanVar()
                if has_default:
                    checkbox_var.set(default_value)
                label.grid(row=ci, column=0, padx=pdx, pady=pdy, sticky='E')
                checkbox = tk.Checkbutton(frame, variable=checkbox_var)
                checkbox.grid(row=ci, column=1)
                widgets[fld.name] = lambda cbv=checkbox_var: cbv.get()
            elif get_origin(type_of) is Literal:
                literal_values = get_args(type_of)
                literal_values_str = tuple(str(s) for s in literal_values)
                if len(set(literal_values_str)) != len(literal_values_str):
                    raise ValueError("Literal has duplicates")
                # print(literal_values)

                label.grid(row=ci, column=0, padx=pdx, pady=pdy, sticky='E')
                if len(literal_values_str) == 0:
                    raise ValueError("GUI error: Literal has zero options")
                default_value = literal_values_str[0] if not has_default else default_value
                sv = tk.StringVar()
                sv.set(default_value)
                dropdown = tk.OptionMenu(frame, sv,
                                         *literal_values)
                dropdown.grid(row=ci, column=1, padx=pdx, pady=pdy)
                widgets[fld.name] = (lambda sv_=sv, lv=literal_values, lvs=literal_values_str:
                                     literal_values[literal_values_str.index(sv_.get())])
            elif type_of is Path:
                label.grid(row=ci, column=0, padx=pdx, pady=pdy, sticky='E')
                current_path = tk.StringVar()
                current_path.set("") if not has_default else current_path.set(str(default_value))
                button_text = tk.StringVar()
                button_text.set("Select File") if not has_default else button_text.set(
                    str(default_value) if str(default_value) != "." else "Select file")
                # ignore this warning about default values being mutable
                button = tk.Button(frame, textvariable=button_text,
                                   command=lambda s=current_path,
                                                  ttl=fld.name,
                                                  btt=button_text,
                                                  meta=metadata: [_select_file(s, ttl, meta),
                                                                  btt.set(_get_path_basename(s.get()))])
                button.grid(row=ci, column=1, padx=10, pady=10)
                widgets[fld.name] = (lambda sv_=current_path: Path(sv_.get()))
            elif get_origin(type_of) is list:
                args_of = get_args(type_of)
                if len(args_of) >= 2:
                    raise ValueError("list[T, T, ...] is illegal")
                c_arg = args_of[0] if len(args_of) >= 1 else str
                # nested list
                if get_origin(c_arg) is list:
                    raise ValueError("Nested lists are not allowed")
                    # inner_args_of = get_args(c_arg)
                    # if len(inner_args_of) >= 2:
                    #     raise ValueError("list[T, T, ...] is illegal")
                    # c_arg_2 = inner_args_of[0] if len(inner_args_of) >= 1 else str
                else:
                    if c_arg not in [str, int, float]:
                        raise ValueError("Lists may only contain str, int, or float")

                    label.grid(row=ci, column=0, padx=pdx, pady=pdy, sticky='E')
                    # c_arg is the argument type
                    lb = _EditableListbox(frame)
                    vsb = tk.Scrollbar(frame, command=lb.yview, orient=tk.VERTICAL)
                    lb.configure(yscrollcommand=vsb.set)
                    vsb.grid(row=ci, column=3)
                    lb.grid(row=ci, column=1, padx=10, pady=10)
                    button = tk.Button(frame, text="+", command=lambda b=lb: b.insert("end", 'CLICK TO EDIT'))
                    button.grid(row=ci, column=2, padx=pdx, pady=pdy)
                    widgets[fld.name] = (lambda lb_=lb, ca=c_arg: [ca(s) for s in lb_.get(0, tk.END)])
                    if has_default:
                        for d in default_value:
                            lb.insert("end", str(d))
            else:
                continue

        dc_val = []
        err_msg = tk.StringVar()
        err_msg.set("")

        exit_state = []

        def on_exit() -> None:
            dc_val.clear()
            try:
                dc_val.append(cls(**{k: v() for k, v in widgets.items()}))  # type: ignore
                if custom_check is not None:
                    st = custom_check(dc_val[0])
                    if st is not None:
                        err_msg.set(st)
                        dc_val.clear()
                        return
                    else:
                        exit_state.append(True)
                        print("exiting")
                        root.quit()
                else:
                    exit_state.append(True)
                    print("exiting")
                    root.quit()
            except ValueError:
                dc_val.clear()
                err_msg.set("Some fields are not the right type (for example, a number field that is not a number)")

        button = tk.Button(frame, text="submit", command=on_exit)
        button.grid(row=len(widgets) + top_offset, column=0, padx=pdx, pady=pdy, columnspan=2)
        err_label = tk.Label(frame, textvariable=err_msg)
        err_label.grid(row=len(widgets) + top_offset + 1, column=0, padx=pdx, pady=pdy, columnspan=2)
        root.mainloop()
        if len(dc_val) == 0 or not exit_state:
            raise KeyboardInterrupt("You closed the UI")
        return dc_val[0]