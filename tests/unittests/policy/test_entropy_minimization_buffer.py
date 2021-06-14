import os,sys
curdir = os.path.dirname(os.path.realpath(__file__))
curdir = curdir.split('/')
curdir = '/'.join(curdir[:-3]) +'/'
os.chdir(curdir)
sys.path.insert(0,curdir)

from utils import Settings
from utils import ContextLogger
from utils import DiaAct
from policy.replay_buffer_entropy_minimization import ReplayBufferEpisode
import traceback

def test_sample_batch_single_full_slice():
    """
    Tests that sample_batch is capable of returning from the history in case a conversation exists
    in the buffer.
    """
    history = ['hello()', 'hello()', 'inform(type=food)', 'request(pricerange)',
            'inform(pricerange=cheap)', 'inform(name=Cafe Cook, type=food, pricerange=cheap)']
    history = map(DiaAct.DiaAct, history)
    conversation_so_far = ['hello()', 'hello()']
    conversation_so_far = map(DiaAct.DiaAct, conversation_so_far)
    expected_response = set([history[-1]])
    Settings.init(config_file='./tests/test_configs/test_entropy_minimization_buffer.cfg')
    ContextLogger.createLoggingHandlers(config=Settings.config)
    logger = ContextLogger.getLogger('')
    logger.info("Starting Entropy Minimization Buffer Test")
    domainString = Settings.config.get('GENERAL', 'domains').split(',')[0]
    em_buffer = ReplayBufferEpisode(domainString, random=Settings.random)
    # Store a mock action list
    em_buffer.store_em_specific(history[:-1], history[-1])

    # emulate a buffer
    em_buffer.episode_em = conversation_so_far

    # Sample a batch, check the output
    batch = em_buffer.sample_batch()
    assert expected_response == batch

def test_sample_batch_multiple_full_slices():
    """
    Tests that sample_batch is capable of returning from the history in case a conversation exists
    in the buffer.
    """
    histories = [
            ['hello()', 'hello()', 'inform(type=food)', 'request(pricerange)',
        'inform(pricerange=cheap)', 'inform(name=Cafe Cook, type=food, pricerange=cheap)'],
            ['hello()', 'hello()', 'inform(type=food)', 'request(pricerange)',
                'inform(pricerange=expensive)',
                'inform(name=Bridges, type=food, pricerange=expensive)'],
    ]
    histories = map(lambda x: map(DiaAct.DiaAct, x), histories)
    conversation_so_far = ['hello()', 'hello()']
    conversation_so_far = map(DiaAct.DiaAct, conversation_so_far)
    expected_response = set([histories[0][-1], histories[1][-1]])
    Settings.init(config_file='./tests/test_configs/test_entropy_minimization_buffer.cfg')
    ContextLogger.createLoggingHandlers(config=Settings.config)
    logger = ContextLogger.getLogger('')
    logger.info("Starting Entropy Minimization Buffer Test")
    domainString = Settings.config.get('GENERAL', 'domains').split(',')[0]
    em_buffer = ReplayBufferEpisode(domainString, random=Settings.random)
    # Store a mock action list
    em_buffer.store_em_specific(histories[0][:-1], histories[0][-1])
    em_buffer.store_em_specific(histories[1][:-1], histories[1][-1])

    # emulate a buffer
    em_buffer.episode_em = conversation_so_far

    # Sample a batch, check the output
    batch = em_buffer.sample_batch()
    assert expected_response == batch

if __name__ == '__main__':
    tests = [test_sample_batch_single_full_slice, test_sample_batch_multiple_full_slices,
            ]
    for test in tests:
        try:
            test()
            print("Succes: " + str(test))
        except Exception, e:
            print("Failed: " + str(test))
            print(traceback.format_exc())

