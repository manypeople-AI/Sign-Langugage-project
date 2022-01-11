from model.seq2seq_lstm import LSTM_Encoder,LSTM_Decoder,LSTM_Seq2Seq
from model.seq2seq_gru_attention import GRU_AT_Decoder, GRU_AT_Encoder, GRU_AT_Seq2Seq, Attention
from utils.seq2seq_preprocessing import  target_preprocessing
from utils.train_utils import BLEU_Evaluate_test,init_weights
import torch
import torch.utils.data as D
import torch.backends.cudnn as cudnn
import random
import numpy as np
import gzip,pickle

import time
import argparse


torch.manual_seed(0)
torch.cuda.manual_seed(0)
torch.cuda.manual_seed_all(0)
np.random.seed(0)
cudnn.benchmark = False
cudnn.deterministic = True
random.seed(0)

        
def main_test(opt):
    
    ### Data Loading
    with gzip.open(opt.X_path + 'X_test.pickle','rb') as f:
        X_data = pickle.load(f)
    excel_name = opt.csv_name # 'C:/Users/winst/Downloads/menmen/train_target.xlsx'
    word_to_index, max_len, vocab,decoder_input = target_preprocessing(excel_name,'test')

    ## Setting of Hyperparameter
    HID_DIM = opt.hid_dim # 512
    OUTPUT_DIM = len(vocab)+1
    N_LAYERS = 2
    DEC_DROPOUT = opt.dropout # 0.5
    emb_dim = opt.emb_dim # 128
    BATCH_SIZE = opt.batch # 32
 
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print('device : ', device)

    ## Change data type
    X_test = torch.tensor(X_data)
    decoder_input = torch.tensor(decoder_input, dtype=torch.long)
    

    dataset = D.TensorDataset(X_test,decoder_input)

    test_dataloader =  torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, drop_last=True)
    
    input_size = 246 # keypoint vector 길이


    ## Define Model
    if opt.model == 'LSTM':
        enc = LSTM_Encoder(input_size, HID_DIM, N_LAYERS)
        dec = LSTM_Decoder(OUTPUT_DIM, emb_dim, HID_DIM, N_LAYERS, DEC_DROPOUT)
        model = LSTM_Seq2Seq(enc, dec, device).to(device)
        model.load_state_dict(torch.load(opt.pt))
    if opt.model == 'GRU':
        enc = GRU_AT_Encoder(input_size, HID_DIM, N_LAYERS)
        att = Attention(HID_DIM)
        dec = GRU_AT_Decoder(OUTPUT_DIM, emb_dim, HID_DIM, N_LAYERS, att, DEC_DROPOUT)
        model = GRU_AT_Seq2Seq(enc,dec,device).to(device)
        model.load_state_dict(torch.load(opt.pt))

    model.apply(init_weights)


    ## Test


    start_time = time.time()


    BLEU = BLEU_Evaluate_test(model,test_dataloader, word_to_index, device, max_len)
    # valid_loss = evaluate(model, val_dataloader, OUTPUT_DIM,criterion)

    end_time = time.time()
    print(end_time - start_time)

    print(f'TEST BLEU : {BLEU : .3f}')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sign-Language-Test')
    parser.add_argument('--X_path',type=str,default='./',help = 'X_test.pikcle path')
    parser.add_argument('--hid_dim', type=int, default=512,help='Number of hidden demension')
    parser.add_argument('--dropout',type=float,default=0.5,help = 'dropout ratio')
    parser.add_argument('--emb_dim',type=int,default=128,help = 'Nuber of embedding demension')
    parser.add_argument('--batch',type=int,default = 32,help='BATCH SIZE')
    parser.add_argument('--pt',type=str,default='model1.pt',help='save model name')
    parser.add_argument('--csv_name',type=str,default='train_target.csv',help='Target Excel name')
    parser.add_argument('--model',type=str,default='GRU',help='[LSTM,GRU]')
    opt = parser.parse_args()
    main_test(opt)
