import logging
log = logging.getLogger(__name__)

def library(name, library, **kwargs):
    ret = {
            'name': name,
            'result': False if not __opts__['test'] else None,
            'changes': {},
            'comment': '',
        }

    if not __salt__['serviio.update_library'](library, test=True, **kwargs):
        ret.update(comment="Library is already up to date", result=True)
        return ret

    curr_lib = __salt__['serviio.get_library'](**kwargs)
    log.trace("Current library: %s", curr_lib)

    if not __opts__['test']:
        __salt__['serviio.update_library'](library, **kwargs)
        updated_lib = __salt__['serviio.get_library'](**kwargs)

    old = {folder['folderPath']: folder for folder in curr_lib}
    new = {folder['folderPath']: folder for folder in (updated_lib if not __opts__['test'] else library)}
    log.trace("Original library options: %s", old)
    log.trace("Updated library options: %s", new)

    ret['changes'] = {f: {
            'old': old[f] if f in old else None,
            'new': new[f] if f in new else None
            } for f in list(set(old.keys()) | set(new.keys()))
                if f not in old or f not in new or old[f] != new[f]}

    ret.update(comment="Library has been updated", result=True)
    return ret
