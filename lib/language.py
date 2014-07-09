from pyretic.core import util
from pyretic.core.network import *
from pyretic.core.util import frozendict, singleton
from pyretic.core.language import *


class match_prefixes_set(DerivedPolicy, Filter):

    """ SDX utilities. Maintain a set of IP prefixes.
        Only useful in the first stages of the SDX compilation."""

    def __init__(self, pfxes):

        if isinstance(pfxes, set):
            self.pfxes = pfxes
        else:
            self.pfxes = set(pfxes)
        super(match_prefixes_set, self).__init__(passthrough)

    def __repr__(self):
        return "match_prefix_set:\n%s" % util.repr_plus([self.pfxes])
