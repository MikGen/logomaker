from __future__ import division, print_function
import numpy as np
import pandas as pd
import ast
import inspect
import re
import sys
import numbers
import matplotlib.pyplot as plt
import numbers
import pdb
import os
from logomaker import ControlledError, check

from six import string_types


from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.lines import Line2D
#from character import font_manager
from logomaker.character import font_manager

# Need for testing colors
#import color
from logomaker import color
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, to_rgba

import warnings

# Specifies IUPAC string transformations
iupac_dict = {
    'A': 'A',
    'C': 'C',
    'G': 'G',
    'T': 'T',
    'R': 'AG',
    'Y': 'CT',
    'S': 'GC',
    'W': 'AT',
    'K': 'GT',
    'M': 'AC',
    'B': 'CGT',
    'D': 'AGT',
    'H': 'ACT',
    'V': 'ACG',
    'N': 'ACGT'
}

# Revise warning output to just show warning, not file name or line number
def _warning(message, category = UserWarning, filename = '', lineno = -1):
    print('Warning: ' + str(message), file=sys.stderr)

# Comment this line if you want to see line numbers producing warnings
warnings.showwarning = _warning

# Comment this line if you don't want to see warnings multiple times
# warnings.simplefilter('always', UserWarning)


def _try_some_code(code_lines, **kwargs):
    """
    Returns True if any of the supplied lines of code do not throw an error.
    """
    is_valid = False
    for code_line in code_lines:
        try:
            exec(code_line)
            is_valid = True
        except:
            pass
    return is_valid

#
# Parameter specifications
#

# Valid values for matrix_type and logo_type
LOGOMAKER_TYPES = {'counts', 'probability', 'enrichment', 'information'}

# Names of parameters that can take on any float value
params_with_float_values = {
    'xtick_anchor',
    'xtick_rotation',
    'ytick_rotation',
    'character_zorder',
    'highlight_zorder',
    'fullheight_zorder',
    'baseline_zorder',
    'vline_zorder',
    'scalebar_x',
    'scalebar_ymin',
    'scalebar_textrotation',
}

# Names of numerical parameters that must be > 0
params_greater_than_0 = {
    'dpi',
    'xtick_spacing',
    'max_positions_per_line',
}

# Names of numerical parameters that must be >= 0
params_greater_or_equal_to_0 = {
    'pseudocount',
    'counts_threshold',
    'character_edgewidth',
    'character_boxedgewidth',
    'highlight_edgewidth',
    'highlight_boxedgewidth',
    'fullheight_edgewidth',
    'fullheight_boxedgewidth',
    'max_alpha_val',
    'hpad',
    'vpad',
    'gridline_width',
    'baseline_width',
    'vline_width',
    'xtick_length',
    'ytick_length',
    'scalebar_length',
    'scalebar_linewidth',
}

# Names of numerical parameters in the interval [0,1]
params_between_0_and_1 = {
    'character_alpha',
    'character_edgealpha',
    'character_boxalpha',
    'character_boxedgealpha',
    'highlight_alpha',
    'highlight_edgealpha',
    'highlight_boxalpha',
    'highlight_boxedgealpha',
    'fullheight_alpha',
    'fullheight_edgealpha',
    'fullheight_boxalpha',
    'fullheight_boxedgealpha',
    'below_shade',
    'below_alpha',
    'width',
    'fullheight_width',
    'vsep',
    'fullheight_vsep',
    'gridline_alpha',
    'baseline_alpha',
}

# Names of parameters allowed to take on a small number of specific values
params_with_values_in_dict = {
    'matrix_type': LOGOMAKER_TYPES,
    'logo_type': LOGOMAKER_TYPES,
    'background_mattype': ['counts', 'probability'],
    'enrichment_logbase': [2, np.e, 10],
    'information_units': ['bits', 'nats'],
    'sequence_type': ['dna', 'DNA',
                      'rna', 'RNA',
                      'protein', 'PROTEIN'],
    'stack_order': ['big_on_top',
                    'small_on_top',
                    'fixed_going_up',
                    'fixed_going_down'],
    'axes_type': ['classic',
                  'naked',
                  'everything',
                  'rails',
                  'vlines',
                  'scalebar'],
    'gridline_axis': ['x', 'y', 'both'],
}

# Names of parameters whose values are True or False
params_with_boolean_values = {
    'center_columns',
    'draw_now',
    'use_transparency',
    'below_flip',
    'uniform_stretch',
    'show_gridlines',
    'show_baseline',
    'show_binary_yaxis',
    'left_spine',
    'right_spine',
    'top_spine',
    'bottom_spine',
    'use_tightlayout',
    'show_position_zero',
    'remove_flattened_characters',
    'csv_delim_whitespace',
    'highlight_bgconsensus',
    'negate_matrix',
    'show_scalebar',
}

# Names of parameters whose values are strings
params_with_string_values = {
    'meme_motifname',
    'save_to_file',
    'characters',
    'ignore_characters',
    'highlight_sequence',
    'max_stretched_character',
    'style_sheet',
    'xtick_format',
    'xlabel',
    'ytick_format',
    'ylabel',
    'title',
    'csv_delimiter',
    'scalebar_text',
    'scalebar_texthalignment',
    'scalebar_textvalignment'
}

# Names of parameters whose values specify a numerical interval
params_that_specify_intervals = {
    'position_range',
    'xlim',
    'ylim'
}

# Names of parameters whose values are ordered numerical arrays
params_that_are_ordered_arrays = {
    'xticks',
    'yticks'
}

# Names of parameters that specify color schemes
params_that_specify_colorschemes = {
    'character_colors',
    'character_edgecolors',
    'character_boxcolors',
    'character_boxedgecolors',
    'highlight_colors',
    'highlight_edgecolors',
    'highlight_boxcolors',
    'highlight_boxedgecolors',
    'fullheight_colors',
    'fullheight_edgecolors',
    'fullheight_boxcolors',
    'fullheight_boxedgecolors',
}

# Names of parameters that specify colors:
params_that_specify_colors = {
    'gridline_color',
    'baseline_color',
    'vline_color',
    'scalebar_color',
}


# Names of parameters that specify fontsize
params_that_specify_FontProperties = {
    'font_file': 'fname',
    'font_family': 'family',
    'font_weight': 'weight',
    'font_style': 'style',

    'axes_fontfile': 'fname',
    'axes_fontfamily': 'family',
    'axes_fontweight': 'weight',
    'axes_fontstyle': 'style',
    'axes_fontsize': 'size',

    'tick_fontfile': 'fname',
    'tick_fontfamily': 'family',
    'tick_fontweight': 'weight',
    'tick_fontstyle': 'style',
    'tick_fontsize': 'size',

    'label_fontfile': 'fname',
    'label_fontfamily': 'family',
    'label_fontweight': 'weight',
    'label_fontstyle': 'style',
    'label_fontsize': 'size',

    'title_fontfile': 'fname',
    'title_fontfamily': 'family',
    'title_fontweight': 'weight',
    'title_fontstyle': 'style',
    'title_fontsize': 'size',
}

params_that_specify_linestyles = {
    'gridline_style',
    'baseline_style',
    'vline_style',
}

# Names of parameters that cannot have None value
params_that_cant_be_none = {
    'pseudocount',
    'enrichment_logbase',
    'center_columns',
    'information_units',
    'draw_now',
    'colors',
    'alpha',
    'edgecolors',
    'edgealpha',
    'edgewidth',
    'boxcolors',
    'boxalpha',
    'boxedgecolors',
    'boxedgealpha',
    'boxedgewidth',
    'stack_order',
    'use_transparency',
    'below_shade',
    'below_alpha',
    'below_flip',
    'hpad',
    'vpad',
    'width',
    'uniform_stretch',
    'axes_type',
    'rcparams',
    'xtick_anchor',
    'use_tightlayout',
    'show_position_zero',
    'highlight_bgconsensus',
    'negate_matrix'
}

# Parameters that specify tick labels
params_that_specify_ticklabels = {
    'xticklabels',
    'yticklabels',
}

# Parameters that specify file names
params_that_specify_filenames = {
    'fasta_file',
    'meme_file',
    'sequences_csvfile',
    'background_seqcsvfile',
    'matrix_csvfile',
    'background_matcsvfile'
}

# Parameters that specify dictionaries
params_that_specify_dicts = {
    'character_style_dict',
    'highlight_style_dict',
    'fullheight_style_dict',
    'font_style_dict',
    'scalebar_dict',
    'gridline_param_dict',
    'baseline_param_dict',
    'rcparams',
    'csv_kwargs',
    'background_csvkwargs'
}

# Names of parameters to leave for later validatation
params_for_later_validation = {
    'background',
    'ct_col',
    'background_ctcol',
    'seq_col',
    'background_seqcol',
    'csv_index_col',
    'csv_header',
    'csv_usecols',
}


#
# Primary validation function
#


def validate_parameter(name, user, default):
    """
    Validates any parameter passed to make_logo or Logo.__init__.
    If user is valid of parameter name, silently returns user.
    If user is invalid, issues warning and retuns default instead
    """

    # Skip if value is none
    if user is None:
        # the second condition is added to avoid mutable argument bugs for dictionaries
        # simply: when dicts are not set by the user, the following will validate/populate with defaults

        if name in params_that_cant_be_none and name not in params_that_specify_dicts:
            raise ValueError("Parameter '%s' cannot be None." % name)

        # this implementation is here to avoid the buggy
        # implementation earlier for mutable arguments in make_logo
        elif name in params_that_specify_dicts:

            value = _validate_dict(name, user, default)
        else:
            value = user

    # Special case: enrichment_logbase: validate as string
    elif name == 'enrichment_logbase':
        str_to_num_dict = {'2': 2, '10': 10, 'e': np.e}
        if isinstance(user, str):
            user = str_to_num_dict[user]
        value = _validate_in_set(name, user, default,
                               params_with_values_in_dict[name])

    #  If value is in a set
    elif name in params_with_values_in_dict:
        value = _validate_in_set(name, user, default,
                                 params_with_values_in_dict[name])

    # If value is boolean
    elif name in params_with_boolean_values:
        value = _validate_bool(name, user, default)

    # If value is str
    elif name in params_with_string_values:
        value = _validate_str(name, user, default)

    # If value is float
    elif name in params_with_float_values:
        value = _validate_number(name, user, default)

    # If value is float > 0
    elif name in params_greater_than_0:
        value = _validate_number(name, user, default,
                                 greater_than=0.0)

    # If value is float >= 0
    elif name in params_greater_or_equal_to_0:
        value = _validate_number(name, user, default,
                                 greater_than_or_equal_to=0.0)

    # If value is float in [0,1]
    elif name in params_between_0_and_1:
        value = _validate_number(name, user, default,
                                 greater_than_or_equal_to=0.0,
                                 less_than_or_equal_to=1.0)

    # If value is an interval
    elif name in params_that_specify_intervals:
        value = _validate_array(name, user, default, length=2)

    # If value is an ordered array
    elif name in params_that_are_ordered_arrays:
        value = _validate_array(name, user, default, increasing=True)

    # If value specifies a color scheme
    elif name in params_that_specify_colorschemes:
        value = _validate_colorscheme(name, user, default)

    # If value specifies a color
    elif name in params_that_specify_colors:
        value = _validate_color(name, user, default)

    # If value specifies FontProperties object
    elif name in params_that_specify_FontProperties:
         passedas = params_that_specify_FontProperties[name]
         value = _validate_FontProperties_parameter(name, user, default,
                                                    passedas=passedas)

    # If value specifies a linestyle
    elif name in params_that_specify_linestyles:
        value = _validate_linestyle(name, user, default)

    # If value specifies ticklabels
    elif name in params_that_specify_ticklabels:
        value = _validate_ticklabels(name, user, default)

    # If value specifies a filename
    elif name in params_that_specify_filenames:
        value = _validate_filename(name, user, default)

    # If value specifies a dicitionary (and user is None)

    elif name in params_that_specify_dicts:
        # checking params when user value for dict is not none
        value = _validate_dict(name, user, default)

    # Special case: shift_first_position_to
    elif name == 'shift_first_position_to':
        value = _validate_number(name, user, default, is_int=True)

    # Special case: max_positions_per_line
    elif name in {'max_positions_per_line', 'meme_motifnum'}:
        value = _validate_number(name, user, default, is_int=True,
                                 greater_than=0)

    # Special case: iupac_string
    elif name == 'iupac_string':
        value = _validate_iupac(name, user, default)

    # Special case: matrix
    elif name == 'dataframe':
        value = validate_dataframe(user, allow_nan=True)

    # Special case: figsize
    elif name == 'figsize':
        value = _validate_array(name, user, default, length=2)

    # Special case: vline_positions
    elif name == 'vline_positions':
        value = _validate_array(name, user, default)

    # Special case: fullheight
    elif name == 'fullheight':

        # Verify is a dictionary
        value = _validate_fullheight(name, user, default)

    # Parameters left for validation later on
    elif name in params_for_later_validation:
        value = user

    # Otherwise, warn if parameter passed through all filters
    else:
        warnings.warn("'%s' parameter not validated." % name, UserWarning)
        value = user


    return value

#
# Private validation functions
#


def _validate_number(name,
                     user,
                     default,
                     is_int=False,
                     greater_than=-np.Inf,
                     greater_than_or_equal_to=-np.Inf,
                     less_than=np.Inf,
                     less_than_or_equal_to=np.Inf,
                     in_set=None):
    """ Validates a floating point parameter. """

    # Test whether parameter can be interpreted as a float
    try:
        # If converting to int
        if is_int:
            value = int(user)

        # Otherwise, if converting to float
        else:
            value = float(user)

    except (ValueError, TypeError):
        value = default
        message = "Cannot interpret value %s for parameter '%s' as number. " +\
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(default))
        warnings.warn(message, UserWarning)

    # Test inequalities
    if not value > greater_than:
        value = default
        message = "Value %s for parameter '%s' is not greater than %s. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(greater_than),
                             repr(default))
        warnings.warn(message, UserWarning)

    elif not value >= greater_than_or_equal_to:
        value = default
        message = "Value %s for parameter '%s' is not greater or equal to %s." + \
                  " Using default value %s instead."
        message = message % (repr(user), name, repr(greater_than_or_equal_to),
                             repr(default))
        warnings.warn(message, UserWarning)

    elif not value < less_than:
        value = default
        message = "Value %s for parameter '%s' is not less than %s. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(less_than),
                             repr(default))
        warnings.warn(message, UserWarning)

    elif not value <= less_than_or_equal_to:
        value = default
        message = "Value %s for parameter '%s' is not less or equal to %s. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(less_than_or_equal_to),
                             repr(default))
        warnings.warn(message, UserWarning)

    elif (in_set is not None) and not (value in in_set):
        value = default
        message = "Value %s for parameter '%s' is not within the set. " + \
                  "of valid values %s. Using default value %s instead."
        message = message % (repr(user), name, repr(in_set),
                             repr(default))
        warnings.warn(message, UserWarning)

    return value


def _validate_bool(name, user, default):
    """ Validates a boolean parameter parameter. """

    # Convert to bool if string is passed
    #if isinstance(user, basestring):
    if isinstance(user, string_types):
        if user == 'True':
            user = True
        elif user == 'False':
            user = False
        else:
            user = default
            message = "Parameter '%s', if string, must be " + \
                      "'True' or 'False'. Using default value %s instead."
            message = message % (name, repr(default))
            warnings.warn(message, UserWarning)

    # Test whether parameter is already a boolean
    # (not just whether it can be interpreted as such)
    if isinstance(user, bool):
        value = user

    # If not, return default value and raise warning
    else:
        value = default
        message = "Parameter '%s' assigned a non-boolean value. " +\
                  "Using default value %s instead."
        message = message % (name, repr(default))
        warnings.warn(message, UserWarning)

    return value


def _validate_in_set(name, user, default, in_set):
    """ Validates a parameter with a finite number of valid values. """

    # If user is valid, use that
    if user in in_set:
        value = user

    # Otherwise, if user is string, try evaluating as literal
    #elif isinstance(user, basestring):
    elif isinstance(user, string_types):
        try:
            tmp = ast.literal_eval(user)
            if tmp in in_set:
                value = tmp

        except:
            value = default
            message = "Invalid value %s for parameter '%s'. " + \
                      "Using default value %s instead."
            message = message % (repr(user), name, repr(default))
            warnings.warn(message, UserWarning)

    # If user value is not valid, set to default and issue warning
    else:
        value = default
        message = "Invalid value %s for parameter '%s'. " + \
                           "Using default value %s instead."
        message = message % (repr(user), name, repr(default))
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_str(name, user, default):
    """ Validates a string parameter. """

    # Test whether parameter can be interpreted as a string
    try:
        value = str(user)

    # If user value is not valid, set to default and issue warning
    except ValueError:
        value = default
        message = "Cannot interpret value %s for parameter '%s' as string. " +\
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(default))
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value

def _validate_iupac(name, user, default):
    """ Validates an IUPAC string """

    message = None

    # Check that user input is a string
    if not isinstance(user, string_types):
        value = default
        message = "Value %s for parameter '%s' is not a string. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(default))

    # Make sure string has nonzero length
    elif len(user) == 0:
        value = default
        message = "String %s, set for parameter '%s', is empty. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(default))

    # Make sure string contains valid characters
    elif not set(list(user.upper())) <= set(iupac_dict.keys()):
        value = default
        message = "String %s, set for parameter '%s', contains " + \
                  "invalid characters. Using default value %s instead."
        message = message % (repr(user), name, repr(default))

    # Make sure string is all capitals
    elif any([c == c.lower() for c in list(user)]):
        value = user.upper()
        message = "String %s, set for parameter '%s', contains lowercase " + \
                  "characters. Using capitalized characters instead."
        message = message % (repr(user), name)

    # If all tests pass, use user input
    else:
        value = user

    if message is not None:
        warnings.warn(message, UserWarning)

    return value


def _validate_filename(name, user, default):
    """ Validates a string parameter. """

    # Test whether file exists and can be opened
    message = None
    try:

        if not os.path.isfile(user):
            value = default
            message = "File %s passed for parameter '%s' does not exist. " +\
                      "Using default value %s instead."
            message = message % (repr(user), name, repr(default))

        elif open(user, 'r'):
            value = user
        else:
            value = default
            message = "File %s passed for parameter '%s' cannot be opened." + \
                      " Using default value %s instead."
            message = message % (repr(user), name, repr(default))

    except (ValueError,TypeError):
        value = default
        if message is None:
            message = "Value %s passed for parameter '%s' is invalid." + \
                      " Using default value %s instead."
            message = message % (repr(user), name, repr(default))

    if message is not None:
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_fullheight(name, user, default):
    """ Validates a fullheight specificaiton, which can be either
     a dictionary or an array/list. """

    # Test whether parameter can be interpreted as a string
    if isinstance(user, string_types):
        user = ast.literal_eval(user)

    # If dictionary
    if isinstance(user, dict):

        # Make sure keys are ints and vals are length 1 strings
        keys = [int(k) for k in user.keys()]
        vals = [str(v) for v in user.values()]

        assert all([len(v) == 1 for v in vals]), \
         'Error: multiple characters passed to single position in fullheight'

        value = dict(zip(keys, vals))

    # If list
    elif isinstance(user, (list, np.array)):
        value = np.array(user).astype(int)

    else:
        value = default
        message = "Invalid value %s for parameter %s. " +\
                  "Using default %s instead."
        message = message % (repr(user), name, repr(default))
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_array(name, user, default, length=None, increasing=False):
    """ Validates an array of numbers. """

    try:
        # If string, convert to list of numbers
        if isinstance(user, string_types):
            user = ast.literal_eval(user)

        if length is not None:
            assert len(user) == length

        for i in range(len(user)):
            user[i] = float(user[i])

        if increasing:
            for i in range(1, len(user)):
                assert user[i - 1] < user[i]

        value = np.array(user).copy()

    except (AssertionError, ValueError):
        value = default
        message = "Improper value %s for parameter '%s'. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(default))
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_colorscheme(name, user, default):
    """ Tests whether user input can be interpreted as a colorschme. """

    # Check whether any of the following lines of code execute without error
    code_lines = [
        'color.color_scheme_dict[user]',
        'plt.get_cmap(user)',
        'to_rgb(user)',
        'color.expand_color_dict(user)'
    ]

    # Test lines of code
    is_valid = False
    for code_line in code_lines:
        try:
            eval(code_line)
            is_valid = True
        except:
            pass

    # For some reason, this needs to be tested separately.
    if user == 'random':
        is_valid = True

    # If so, then colorscheme is valid
    if is_valid:
        value = user

    # Otherwise, use default colorscheme
    else:
        value = default
        message = "Improper value %s for parameter '%s'. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(default))
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_color(name, user, default):
    """ Tests whether user input can be interpreted as an RGBA color. """

    # Check whether any of the following lines of code execute without error
    try:
        to_rgba(user)
        is_valid = True
    except ValueError:
        is_valid = False

    # If so, then colorscheme is valid
    if is_valid:
        value = user

    # Otherwise, use default colorscheme
    else:
        value = default
        message = "Improper value %s for parameter '%s'. " + \
                  "Using default value %s instead."
        message = message % (repr(user), name, repr(default))
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_FontProperties_parameter(name, user, default, passedas):
    """ Validates any parameter passed to the FontProperties constructor. """

    try:
        # Create a FontProperties object and try to use it for something
        prop = FontProperties(**{passedas:user})
        TextPath((0,0), 'A', size=1, prop=prop)

        value = user
    except ValueError:
        value = default
        message = ("Invalid string specification '%s' for parameter '%s'. "
                   + "Using default value %s instead.") \
                  % (user, name, default)
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_linestyle(name, user, default):
    """ Validates any parameter that specifies a linestyle. """

    try:
        # Create a FontProperties object and try to use it for something
        Line2D((0, 1), (0, 1), linestyle=user)
        value = user

    except (ValueError, TypeError):
        value = default
        message = ("Invalid string specification '%s' for parameter '%s'. "
                   + "Using default value %s instead.") \
                  % (user, name, default)
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def _validate_dict(name, user, default):
    """ Validates any parameter that specifies a dictionary. """

    # if dict set by user
    if(user is not None):

        if type(user) == dict:
            value = user
            _validate_user_set_dict(name, user)

        else:
            message = "%s = %s is not a dictionary. Using %s instead." \
                      % (name, repr(user), repr(default))
            warnings.warn(message, UserWarning)
            value = default

    # if none, then return dict populated with default values
    # i.e., if not set by user
    else:

        value = _populate_default_dict_value(name,user)

    # Return valid value to user
    return value


def _validate_ticklabels(name, user, default):
    """ Validates parameters passed as tick labels. """

    message = None
    # Check that user can be read as list
    try:
        user = list(user)
    except TypeError:
        message = ("Cant interpret value '%s' for parameter '%s' as list. "
                   + "Using default value %s instead.") \
                  % (user, name, default)

    # Test that elements of user are strings or numbers
    tests = [isinstance(u, string_types) or isinstance(u, numbers.Number) \
                for u in user]
    if len(tests) > 0 and not all(tests):
        message = ("Cant interpret all elements of '%s', "
                   + "assigned to parameter '%s', as string or number. "
                   + "Using default value %s instead.") \
                  % (user, name, default)

    # If any errors were encountered, use default as value and display warning
    # Otherwise, use user input as value.
    if message is None:
        value = user
    else:
        value = default
        warnings.warn(message, UserWarning)

    # Return valid value to user
    return value


def validate_dataframe(dataframe, allow_nan=True):
    '''
    Runs checks to verify that df is indeed a motif dataframe.
    Returns a cleaned-up version of df if possible
    '''

    check(isinstance(dataframe,pd.DataFrame),
          'Input Error: dataframe needs to be a valid pandas dataframe, dataframe entered: '+str(type(dataframe)))

    # Copy and preserve logomaker_type
    dataframe = dataframe.copy()

    if not allow_nan:
        # Make sure all entries are finite numbers
        check(np.isfinite(dataframe.values).all(),'Input Error: some matrix elements are not finite.' + 'Set allow_nan=True to allow.')

    # Make sure the matrix has a finite number of rows and columns
    check(dataframe.shape[0] >= 1, 'Input Error: matrix has zero rows.')
    check(dataframe.shape[1] >= 1, 'Input Error: matrix has zero columns.')

    # Remove columns whose names aren't strings exactly 1 character long.
    # Warn user when doing so
    cols = dataframe.columns
    for col in cols:
        if not isinstance(col, string_types) or (len(col) != 1):
            del dataframe[col]
            message = ('Matrix has invalid column name "%s". This column ' +
                       'has been removed.') % col
            warnings.warn(message, UserWarning)

    cols = dataframe.columns
    for i, col_name in enumerate(cols):
        # Ok to have a 'pos' column
        if col_name == 'pos':
            continue

        # Convert column name to simple string if possible
        check(isinstance(col_name, string_types), 'Error: column name %s is not a string' % col_name)
        new_col_name = str(col_name)

        # If column name is not a single chracter, try extracting single character
        # after an underscore
        if len(new_col_name) != 1:
            new_col_name = new_col_name.split('_')[-1]
            check((len(new_col_name)==1),'Error: could not extract single character from colum name %s'%col_name)

        # Make sure that colun name is not a whitespace character
        check(re.match('\S',new_col_name),'Error: column name "%s" is a whitespace charcter.'%repr(col_name))

        # Set revised column name
        dataframe.rename(columns={col_name:new_col_name}, inplace=True)

    # If there is a pos column, make that the index
    if 'pos' in cols:
        dataframe['pos'] = dataframe['pos'].astype(int)
        dataframe.set_index('pos', drop=True, inplace=True)

    # Remove name from index column
    dataframe.index.names = [None]

    # Alphabetize character columns
    char_cols = list(dataframe.columns)
    char_cols.sort()
    dataframe = dataframe[char_cols]

    # Return cleaned-up df
    return dataframe

def validate_probability_mat(matrix):
    '''
    Verifies that the df is indeed a probability motif dataframe.
    Returns a normalized and cleaned-up version of df if possible
    '''

    # Validate as motif
    matrix = validate_dataframe(matrix)

    # Validate df values as info values
    assert (all(matrix.values.ravel() >= 0)), \
        'Error: not all values in df are >=0.'

    # Normalize across columns
    matrix.loc[:, :] = matrix.values / matrix.values.sum(axis=1)[:, np.newaxis]

    return matrix


# Implementation note: this method should contain a list of the valid keys of any dictionary
# that can be entered as a parameter for logomaker
def _validate_user_set_dict(dict_name,dictionary_with_keys_vals):

    if(dict_name=='character_style_dict'):

        valid_dict_keys = [
            'character_colors',
            'character_alpha',
            'character_edgecolors',
            'character_edgealpha',
            'character_edgewidth',
            'character_boxcolors',
            'character_boxedgecolors',
            'character_boxedgewidth',
            'character_boxalpha',
            'character_boxedgealpha',
            'character_zorder'
        ]
    elif(dict_name=='highlight_style_dict'):

        valid_dict_keys = [
            'highlight_sequence',
            'highlight_bgconsensus',
            'highlight_colors',
            'highlight_alpha',
            'highlight_edgecolors',
            'highlight_edgewidth',
            'highlight_edgealpha',
            'highlight_boxcolors',
            'highlight_boxalpha',
            'highlight_boxedgecolors',
            'highlight_boxedgewidth',
            'highlight_boxedgealpha',
            'highlight_zorder'
        ]

    elif(dict_name=='fullheight_style_dict'):

        valid_dict_keys = [
            'fullheight',
            'fullheight_colors',
            'fullheight_alpha',
            'fullheight_edgecolors',
            'fullheight_edgewidth',
            'fullheight_edgealpha',
            'fullheight_boxcolors',
            'fullheight_boxalpha',
            'fullheight_boxedgecolors',
            'fullheight_boxedgewidth',
            'fullheight_boxedgealpha',
            'fullheight_zorder',
            'fullheight_vsep',
            'fullheight_width'
        ]

    elif(dict_name=='font_style_dict'):

        valid_dict_keys = [
            'font_properties',
            'font_file = None',
            'font_family',
            'font_weight',
            'font_style',
        ]

    elif(dict_name=='scalebar_dict'):

        valid_dict_keys = [
            'show_scalebar',
            'scalebar_length',
            'scalebar_linewidth',
            'scalebar_color',
            'scalebar_text',
            'scalebar_x',
            'scalebar_ymin',
            'scalebar_texthalignment',
            'scalebar_textvalignment',
            'scalebar_textrotation',
        ]

    elif(dict_name=='gridline_param_dict'):

        valid_dict_keys = [
            'show_gridlines',
            'gridline_axis',
            'gridline_width',
            'gridline_color',
            'gridline_alpha',
            'gridline_style',
        ]

    elif(dict_name=='baseline_param_dict'):

        valid_dict_keys = [
            'show_baseline',
            'baseline_width',
            'baseline_color',
            'baseline_alpha',
            'baseline_style',
            'baseline_zorder',
        ]


    # need to fill condition for rcParams

    # if invalid key found, pop key.
    #for k in dictionary_with_keys_vals.keys(): # this doesn't work with python 3
    for k in list(dictionary_with_keys_vals):
        if (k not in valid_dict_keys):
            #warnings.warn(" Invalid key '%s' for %s, removing invalid key... " %(k,dict_name), UserWarning)
            print("Warning: Invalid key '%s' for %s, removing invalid key... " %(k,dict_name))
            dictionary_with_keys_vals.pop(k)

    # find keys that the user did not provide and set them to defaults
    keys_not_set_by_user = list(set(dictionary_with_keys_vals).symmetric_difference(valid_dict_keys))

    # populate the missing keys with default values
    if (len(keys_not_set_by_user) > 0):
        _populate_default_dict_value(dict_name, dictionary_with_keys_vals, dict_set_by_user=True,
                                     keys_not_set_by_user=keys_not_set_by_user)

    else:
        return dictionary_with_keys_vals


# method that gets called if dictionaries aren't user supplied
# so they may be populated with default values.
# Implementation note: this needs to contain default dictionary key/values
def _populate_default_dict_value(dict_name,dictionary_with_keys_vals,dict_set_by_user=False,keys_not_set_by_user=None):

    dict_to_be_populated = {}

    if(dict_name=='character_style_dict'):

        default_character_style_values = {
            'character_colors': 'classic',
            'character_alpha': None,
            'character_edgecolors': None,
            'character_edgealpha': None,
            'character_edgewidth': 1,
            'character_boxcolors': None,
            'character_boxedgecolors': None,
            'character_boxedgewidth': 1,
            'character_boxalpha': None,
            'character_boxedgealpha': None,
            'character_zorder': 3
        }

        # if the user hasn't set the dictionary at all, set all keys to default values
        if(dict_set_by_user==False):
            dict_to_be_populated = default_character_style_values

        # if the user has partially set the dictionary
        elif(dict_set_by_user==True):

            # set the missing key values to defaults
            for missing_key in keys_not_set_by_user:
                dictionary_with_keys_vals[missing_key] = default_character_style_values[missing_key]

    elif (dict_name == 'highlight_style_dict'):

        default_highlight_style_values = {
            'highlight_sequence':None,
            'highlight_bgconsensus':False,
            'highlight_colors':None,
            'highlight_alpha':None,
            'highlight_edgecolors':None,
            'highlight_edgewidth':None,
            'highlight_edgealpha':None,
            'highlight_boxcolors':None,
            'highlight_boxalpha':None,
            'highlight_boxedgecolors':None,
            'highlight_boxedgewidth':None,
            'highlight_boxedgealpha':None,
            'highlight_zorder':None
        }

        # if the user hasn't set the dictionary at all, set all keys to default values
        if (dict_set_by_user == False):
            dict_to_be_populated = default_highlight_style_values
        else:
            for missing_key in keys_not_set_by_user:
                dictionary_with_keys_vals[missing_key] = default_highlight_style_values[missing_key]


    elif (dict_name == 'fullheight_style_dict'):

        default_fullheight_style_values = {
            'fullheight':None,
            'fullheight_colors':None,
            'fullheight_alpha':None,
            'fullheight_edgecolors':None,
            'fullheight_edgewidth':None,
            'fullheight_edgealpha':None,
            'fullheight_boxcolors':None,
            'fullheight_boxalpha':None,
            'fullheight_boxedgecolors':None,
            'fullheight_boxedgewidth':None,
            'fullheight_boxedgealpha':None,
            'fullheight_zorder':None,
            'fullheight_vsep':None,
            'fullheight_width':None
        }

        # if the user hasn't set the dictionary at all, set all keys to default values
        if (dict_set_by_user == False):
            dict_to_be_populated = default_fullheight_style_values
        else:
            for missing_key in keys_not_set_by_user:
                dictionary_with_keys_vals[missing_key] = default_fullheight_style_values[missing_key]


    elif (dict_name == 'font_style_dict'):
        default_font_style_values = {
            'font_properties':None,
            'font_file':None,
            'font_family':('Arial Rounded MT Bold', 'Arial', 'sans'),
            'font_weight':'bold',
            'font_style':None,
        }

        # if the user hasn't set the dictionary at all, set all keys to default values
        if (dict_set_by_user == False):
            dict_to_be_populated = default_font_style_values
        else:
            for missing_key in keys_not_set_by_user:
                dictionary_with_keys_vals[missing_key] = default_font_style_values[missing_key]

    elif(dict_name=='scalebar_dict'):

        default_scalarbar_dict_values = {

                'show_scalebar':None,
                'scalebar_length':None,
                'scalebar_linewidth':None,
                'scalebar_color':None,
                'scalebar_text':None,
                'scalebar_x':None,
                'scalebar_ymin':None,
                'scalebar_texthalignment':None,
                'scalebar_textvalignment':None,
                'scalebar_textrotation':None,
        }

        # if the user hasn't set the dictionary at all, set all keys to default values
        if (dict_set_by_user == False):
            dict_to_be_populated = default_scalarbar_dict_values
        else:
            for missing_key in keys_not_set_by_user:
                dictionary_with_keys_vals[missing_key] = default_scalarbar_dict_values[missing_key]

    elif(dict_name=='gridline_param_dict'):

        default_gridline_dict_values = {

                'show_gridlines':None,
                'gridline_axis':None,
                'gridline_width':None,
                'gridline_color':None,
                'gridline_alpha':None,
                'gridline_style':None,
        }

        # if the user hasn't set the dictionary at all, set all keys to default values
        if (dict_set_by_user == False):
            dict_to_be_populated = default_gridline_dict_values
        else:
            for missing_key in keys_not_set_by_user:
                dictionary_with_keys_vals[missing_key] = default_gridline_dict_values[missing_key]

    elif(dict_name=='baseline_param_dict'):

        default_baseline_dict_values = {

            'show_baseline':None,
            'baseline_width':None,
            'baseline_color':None,
            'baseline_alpha':None,
            'baseline_style':None,
            'baseline_zorder':None,
        }

        # if the user hasn't set the dictionary at all, set all keys to default values
        if (dict_set_by_user == False):
            dict_to_be_populated = default_baseline_dict_values
        else:
            for missing_key in keys_not_set_by_user:
                dictionary_with_keys_vals[missing_key] = default_baseline_dict_values[missing_key]

    elif (dict_name == 'rcparams'):
        dict_to_be_populated = {}


    return dict_to_be_populated