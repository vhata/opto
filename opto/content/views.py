import logging
import os
import posixpath
import urllib

from django.conf import settings
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render


log = logging.getLogger(__name__)

def serve_content(request, path, document_root):
    index_name = settings.CONTENT_INDEX_NAME
    ignore_prefix = settings.CONTENT_IGNORE_PREFIX
    filetypes = settings.CONTENT_FILETYPES

    # Stripping the left '/' and applying normpath means normalized_path will be
    # the most succinct path relative to the current directory, with all '.',
    # '..', and '//' removed or simplified.
    normalized_path = posixpath.normpath(urllib.unquote(path)).lstrip('/')
    log.debug('Requested: %s', normalized_path)

    # The above operation means that if the normalized path is attempting to go
    # above the level of the specified document_root, it will have been
    # simplified enough to directly begin with '../' - this is a security
    # violation and is treated as a bad request.
    if normalized_path.startswith('..'):
        raise Http404('Invalid path.')

    # We only have ASCII filenames
    try:
        normalized_path = str(normalized_path)
    except UnicodeEncodeError:
        raise Http404('Invalid path')

    # # If someone requests <somepath>/<index_file> we need to redirecto them
    # # to just <somepath>/. If we don't, there will be duplicate paths with
    # # the same content which may have negative SEO reprecussions.
    #
    # I think that's bullshit.
    #
    # if os.path.basename(normalized_path) in index_name:
    #     path = request.META['PATH_INFO']
    #     path = path[:path.rfind(os.path.basename(normalized_path))]
    #     return HttpResponseRedirect(path)

    if (ignore_prefix and
            os.path.basename(normalized_path).startswith(ignore_prefix)):
        return HttpResponseForbidden('"%s" may not be accessed' % normalized_path)

    template_path = os.path.join(document_root, normalized_path)

    possible_path = template_path
    if os.path.isdir(template_path):
        for index in index_name:
            possible_path = os.path.join(template_path, index)
            log.debug("Looking for %s", possible_path)
            if os.path.exists(possible_path):
                break

    if not os.path.exists(possible_path):
        raise Http404('"%s" does not exist' % normalized_path)

    log.debug("Found %s", possible_path)
    template_path = possible_path

    extension = os.path.splitext(template_path)[1]

    if extension not in filetypes:
        raise Http404('"%s" isn\'t an allowed filetype' % path)

    return render(request, template_path)

