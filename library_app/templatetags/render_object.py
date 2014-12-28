from django import template
from django.template.loader import render_to_string
from django.db.models import Model
from django.utils.safestring import mark_safe

register = template.Library()
BASE_PATH = 'render'


class RenderObjectNode(template.Node):
    def __init__(self, object_ref, position, varname):
        self.object_ref = template.Variable(object_ref)
        if position and position[0] in ('\'', '\"') and position[0] == position[-1]:
            position = position[1:-1]
        self.position = position
        self.varname = varname

    def render(self, context):
        # Retrieve the object from the template context
        try:
            object_ref = self.object_ref.resolve(context)
            assert isinstance(object_ref, Model)
        except (template.VariableDoesNotExist, AssertionError):
            # No context variable found, or variable was not a model
            model_name = None
        else:
            model_name = object_ref._meta.app_label + '_' + object_ref._meta.module_name

        # Construct the template loader list
        templates = []
        if self.position:
            if model_name:
                templates += ['%s/%s/%s.html' % (BASE_PATH, self.position, model_name)]
            templates += ['%s/%s/default.html' % (BASE_PATH, self.position)]
        if model_name:
            templates += ['%s/%s.html' % (BASE_PATH, model_name)]
        templates += ['%s/default.html' % BASE_PATH]

        # Render the object and output it or add it to the template context
        try:
            rendered = render_to_string(templates, {'object': object_ref}, context)
        except template.TemplateDoesNotExist:
            # No template found -- fail silently
            if self.varname:
                context[self.varname] = ''
            return ''
        rendered = mark_safe(rendered)
        if self.varname:
            context[self.varname] = rendered
            return ''
        else:
            return rendered

def do_render_object(parser, token):
    """
    Used to output a rendered representation of a given model object.

    This tag allows you to use standard templates to describe how you want a given
    model to be displayed. Once you have created a rendering template for a model,
    you can simply feed it to the ``render_object`` tag and it will know how to
    output it in your template.

    This is generally useful when you need to render a list of objects of many
    types, or when you need to display an object but don't know ahead of time what
    type it is. For example, if your site search returns a list of objects from
    various models, you can simply loop over them and use ``render_object``.

    Usage::

        {% render_object [object] for "[position]" as [varname] %}

    The ``object`` argument should be a reference to the actual object to be
    rendered. The remaining arguments (described below) are all optional.

    By default, the tag will attempt to render the ``object`` by choosing the first
    template from the following locations::

        "render/[app_label]_[model_name].html"
        "render/default.html"

    If no template is found, the tag will output an empty string. When a template
    is found, it will receive the same context as the original template, plus an
    ``object`` variable which holds the model object.

    If you specify ``for "[position]"``, you can give a single model different
    representations for different locations throughout your site. If you include a
    ``position`` argument, ``render_object`` will add a couple templates to the top
    of the list, like so::

        "render/[position]/[app_label]_[model_name].html"
        "render/[position]/default.html"
        "render/[app_label]_[model_name].html"
        "render/default.html"

    If you specify ``as [varname]``, the tag will place the rendered text into a
    context variable instead of outputting it to the template.
    """
    bits = token.split_contents()
    varname = None
    position = None
    if bits[-2] == 'as':
        # Get the varname, if specified
        varname = bits[-1]
        bits = bits[:-2]
    if bits[-2] == 'for':
        # Get the position, if specified
        position = bits[-1]
        bits = bits[:-2]
    if len(bits) != 2:
        raise template.TemplateSyntaxError("%r tag has two required arguments" % bits[0])
    return RenderObjectNode(bits[1], position, varname)

register.tag('render_object', do_render_object)