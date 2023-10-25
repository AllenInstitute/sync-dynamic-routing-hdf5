import datetime
import logging
import pathlib

import npc_lims
from np_session.components.info import Mouse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename=f'logs/hdf5_sync_{datetime.datetime.today().date()}.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

for session_info in npc_lims.get_session_info():
    if not (t := session_info.training_info):
        continue
    if 'np' in t['rig_name'].lower():
        continue
    subject = Mouse(session_info.subject)
    destfolder = npc_lims.DR_DATA_REPO_ISILON / str(subject.id)
    destfolder.mkdir(exist_ok=True)
    
    glob_pattern = f"DynamicRouting1_{session_info.subject}_{session_info.date.replace('-', '')}_*.hdf5"
    if next(destfolder.glob(glob_pattern), None) is not None:
        continue # already synced
    
    src = next(pathlib.Path('\\' + str(subject.lims.path)).rglob(glob_pattern), None)
    if src is None:
        logger.info(f'No file matching {glob_pattern!r} in {subject.lims.path=}')
        continue
    
    logger.info(f'Copying {src.name}')
    dest = destfolder / src.name
    assert dest.exists() is False, f'{dest.name} already exists'
    dest.write_bytes(s := src.read_bytes())
    assert s == dest.read_bytes(), f'Failed to copy {src.name} correctly'