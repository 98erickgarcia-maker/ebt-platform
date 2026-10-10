import test from 'node:test';
import assert from 'node:assert/strict';
import {validateRequest, guardComposer} from '../../scripts/ops/insert_chat.mjs';

const valid = {url:'https://chatgpt.com/c/00000000-0000-4000-8000-000000000001',
 text:'Proposta sintética FLOW-01', action:'send'};
test('only exact conversation and bounded reviewed text are accepted', () => {
 assert.deepEqual(validateRequest(valid), valid);
 for (const update of [{url:'https://evil.invalid/'}, {url:'https://chatgpt.com/'},
  {url:valid.url+'?secret=private'}, {text:'sk-'+'syntheticNOTREAL123456789'},
  {action:'deploy'}, {text:''}]) assert.throws(() => validateRequest({...valid,...update}));
});
test('busy chat, existing draft and missing Extra High block insertion', () => {
 guardComposer({busy:false,draft:'',extraHigh:true,composer:true});
 for (const update of [{busy:true},{draft:'rascunho do usuário'},{extraHigh:false},{composer:false},{limitNotice:true}])
  assert.throws(() => guardComposer({busy:false,draft:'',extraHigh:true,composer:true,...update}));
});

