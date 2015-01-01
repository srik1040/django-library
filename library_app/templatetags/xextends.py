from django import template
from django.template.loader_tags import do_extends
import tokenize
import StringIO

register = template.Library()

class XExtendsNode(template.Node):
    def __init__(self, node, kwargs):
        self.node = node
        self.kwargs = kwargs

    def render(self, context):
        # TODO: add the values to the bottom of the context stack instead?
        context.update(self.kwargs)
        try:
           return self.node.render(context)
        finally:
           context.pop()

def do_xextends(parser, token):
    """
    Allows to extend specific template, but additionally
    pass certain parameters to it.
    """
    bits = token.contents.split()
    kwargs = {}
    if 'with' in bits:
        pos = bits.index('with')
        argslist = bits[pos+1:]
        bits = bits[:pos]
        for i in argslist:
            try:
                a, b = i.split('=', 1); a = a.strip(); b = b.strip()
                keys = list(tokenize.generate_tokens(StringIO.StringIO(a).readline))
                if keys[0][0] == tokenize.NAME:
                    kwargs[str(a)] = parser.compile_filter(b)
                else: raise ValueError
            except ValueError:
                raise template.TemplateSyntaxError, "Argument syntax wrong: should be key=value"
        # before we are done, remove the argument part from the token contents,
        # or django's extends tag won't be able to handle it.
        # TODO: find a better solution that preserves the orginal token including whitespace etc.
        token.contents = " ".join(bits)

    # let the orginal do_extends parse the tag, and wrap the ExtendsNode
    return XExtendsNode(do_extends(parser, token), kwargs)

register.tag('xextends', do_xextends)