import datetime
import logging
import pathlib

import npc_lims
from np_session.components.info import Mouse
from np_session.databases.data_getters import get_psql_cursor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename=f'logs/hdf5_sync_{datetime.datetime.today().date()}.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

NUM_PREVIOUS_DAYS_TO_SEARCH = 7

if __name__ == "__main__":
    today = datetime.datetime.today().date()
    start_date = today - datetime.timedelta(days=NUM_PREVIOUS_DAYS_TO_SEARCH)
    logger.info(f'finding behvior sessions in lims created since {start_date}')
    cur = get_psql_cursor()
    cur.execute("select storage_directory from behavior_sessions where date_of_acquisition >= %s", (start_date,))
    logger.info(f'found {cur.rowcount} behavior sessions (not all DR)')
    sessions = cur.fetchall()
    for session in sessions:
        glob_pattern = f"DynamicRouting1*.hdf5"
        src = next(pathlib.Path('/' + session['storage_directory']).rglob(glob_pattern), None)
        if src is None:
            continue # not a DR session
        subject = npc_lims.npc_session.extract_subject(src.stem)
        assert subject is not None, f'failed to extract subject from {src}'
        dest = npc_lims.DR_DATA_REPO_ISILON / str(subject) / src.name
        if dest.exists():
            continue # already synced       
        logger.info(f'Copying {src.name}')
        assert dest.exists() is False, f'{dest.name} already exists'
        dest.parent.mkdir(exist_ok=True, parents=True)
        dest.write_bytes(s := src.read_bytes())
        assert s == dest.read_bytes(), f'Failed to copy {src.name} correctly'
        
    logger.info('done')
