# Pyper

Pyper is a relatively simple package to move data around using functional pieces. I noticed that the standard set of functors provided out of the box was not enough, that I was constantly rearranging my data to fit the right shape to apply, say, the map functor. Pyper provides a __super slow__ solution to this problem.

## The fundamental principal

Given a functor from either objects to objects or functions to functions, there is a dual object hidden in plain sight. For example, map takes functions (f : A --> B) to (map(f) : Seq(A) --> Seq(B)). There is a dual to map, namely, a functor which takes a single object and returns a list of those objects, namely x : A becomes map*(x) : Seq(A).

So we basically did this for everything we could think of: objects, sequences, and dictionaries. At the very least, it will be so confusing as to be completely unreadable by Copilot.

## Notation (clunky but sufficient)
To use pyper, you need to help the interpreter continue treating functions as objects so they can be moved around:

```
ON(object).to_dict(
    on_obj.do_fdict.<this_way>(
        f1 = <function>,
        f2 = <function>,
        f3 = <function>
    )
)
```
this says "take an object, treat it like a single object (ON), and change it into a dictionary-like thing as follows:
    take a dictionary of functions {f1 = <>, f2 = <>, f3 = <>} and apply it to object <this_way>." What "this way" is will depend on what is available for the combination of an ON and an fdict (a dictionary of functions). We have pretty much one way of applying a dictionary of functions to an object:

```
x : int = 123
y = ON(x).to_dict(
    on_obj.do_fdict.naturally(
        f1 = lambda m : m + 1,
        f2 = lambda n : 2*n,
        f3 = lambda p : p - 100 
    )
)
print(y)
```
will produce `DN({"f1" : 124, "f2" : 246, "f3" : 23})`. It basically allows you to apply a dictionary of functions to a single object, creating a dictionary with the same keys, and results as values. We can do the opposite as well:
```
x : dict[str, int] = {"a" : 123, "b" : 0, "c" : -10}
y = DN(x).to_dict(
    on_dict.do_func.naturally(
        lambda x : 2*x
    )
)
print(y)
```
will produce `DN({"a" : 246, "b" : 0, "c" : -20})`. It applies a single function to a dictionary, creating a dictionary with the same keys and results as values. (see the symmetry?). Note that we had to start with a `DN` object to let the type checker know that we're using the `on_dict` module. Notice that the first one is `on_obj.do_fdict` and the second one is `on_dict.do_func`. Symmetry.

Let's look at one more, a little more complicated:
```
reports = SN(visits).apply_dictof(
    visit_statuses = on_seq.do_func.naturally(
        lambda v : visit.status
    ),
    correct_visits = on_seq.do_flist.as_filters(
        lambda v : v.has_property1,
        lambda v : v.has_property2,
        lambda v : v.meets_criteria
    ),
).is_dnsn().dnsn_to_dn().data

```
Whew! This is a lot. Let's break it down.
1) Take a list of visits and treat it as a sequence.
2) On that sequence 'pop up' to a dictionary (`DN`) of the following pyper operations:
    - on the sequence of visits, do the following function to each element, ala map: get the visit status. Gives an `SN`.
    - on the sequence of visits, take a list of functions and use them to filter the list as follows: first keep only those with property1, then of those keep only those property2, etc. etc. Gives an `SN`.
3) Check whether the resulting object is a DN of SN's. `is_dnsn()`. The structure of the object is:

```
DN(
    {
        'visit_statuses' = SN([visit statues for each visit]),
        'correct_visits' = SN([visits that meet all those conditions])
    }
)
```
so we're good.

4) Get rid of the inner set of `SN`s.
5) Return the thing inside the outer DN, which is just a dictionary of lists.

## What can I do?
There are nine combinations of objects and function-objects that can be combined in various ways, plus the "apply" pop-up operation, giving you nested data structures (eg, DNSN's, which is a dictionary of sequences).

TBD.


