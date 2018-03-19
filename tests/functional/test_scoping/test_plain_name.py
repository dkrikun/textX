from textx import metamodel_from_str
from textx import get_children
import textx.scoping.providers as scoping_providers
import textx.exceptions
from pytest import raises

metamodel_str = '''
Model:
    packages*=Package
;

Package:
    'package' name=ID '{'
    classes*=Class
    '}'
;

Class:
    'class' name=ID '{'
        attributes*=Attribute
    '}'
;

Attribute:
        'attr' ref=[Class] name=ID ';'
;
'''


def test_plain_name_ref():
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(metamodel_str)

    my_metamodel.register_scope_providers({"*.*": scoping_providers.PlainName(
        multi_metamodel_support=False)})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_metamodel.model_from_str('''
    package P1 {
        class Part1 {
        }
    }
    package P2 {
        class Part2 {
            attr C2 rec;
        }
        class C2 {
            attr Part1 p1;
            attr Part2 p2a;
            attr Part2 p2b;
        }
    }
    ''')

    #################################
    # TEST MODEL
    #################################

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "rec",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "rec"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "C2"

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "p1",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "p1"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part1"

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "p2a",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "p2a"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part2"

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "p2b",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "p2b"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part2"

    ###########################
    # MODEL WITH ERROR (no entry found)
    ############################
    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*Unknown object.*Part0.*'):
        my_model2 = my_metamodel.model_from_str('''
        package P1 {
            class Part1 {
            }
        }
        package P2 {
            class C2 {
                attr Part0 p1;
            }
        }
        ''')

    ###########################
    # MODEL WITH NO ERROR (double entries not checked)
    ############################
    my_model2 = my_metamodel.model_from_str('''
    package P1 {
        class Part1 {
        }
    }
    package P2 {
        class Part1 {
        }
        class C2 {
            attr Part1 p1;
        }
    }
    ''')

    #################################
    # END
    #################################

def test_plain_name_ref_with_muli_metamodel_support():
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(metamodel_str)

    my_metamodel.register_scope_providers({"*.*": scoping_providers.PlainName(
        multi_metamodel_support=True)})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_metamodel.model_from_str('''
    package P1 {
        class Part1 {
        }
    }
    package P2 {
        class Part2 {
            attr C2 rec;
        }
        class C2 {
            attr Part1 p1;
            attr Part2 p2a;
            attr Part2 p2b;
        }
    }
    ''')

    #################################
    # TEST MODEL
    #################################

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "rec",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "rec"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "C2"

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "p1",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "p1"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part1"

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "p2a",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "p2a"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part2"

    a = get_children(lambda x: hasattr(x, 'name') and x.name == "p2b",
                     my_model)
    assert len(a) == 1
    assert a[0].name == "p2b"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part2"

    ###########################
    # MODEL WITH ERROR (no entry found)
    ############################
    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*Unknown object.*Part0.*'):
        my_model2 = my_metamodel.model_from_str('''
        package P1 {
            class Part1 {
            }
        }
        package P2 {
            class C2 {
                attr Part0 p1;
            }
        }
        ''')

    ###########################
    # MODEL WITH ERROR (double entries)
    ############################
    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*None:10:\d+: error: name Part1 is not unique.*'):
        my_model2 = my_metamodel.model_from_str('''
        package P1 {
            class Part1 {
            }
        }
        package P2 {
            class Part1 {
            }
            class C2 {
                attr Part1 p1;
            }
        }
        ''')

    #################################
    # END
    #################################
