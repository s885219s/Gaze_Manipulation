#-*- coding: utf-8 -*-
import argparse

def str2bool(v):
  return v.lower() in ('true', '1')

arg_lists = []
model_config = argparse.ArgumentParser()

# model
model_config.add_argument('--is_cfw_only', type=bool, default=False, help='')
model_config.add_argument('--height', type=eval, default=41, help='')
model_config.add_argument('--width', type=eval, default=51, help='')
model_config.add_argument('--channel', type=eval, default=3, help='')
model_config.add_argument('--ef_dim', type=eval, default=14, help='')
model_config.add_argument('--agl_dim', type=eval, default=2, help='')
model_config.add_argument('--encoded_agl_dim', type=eval, default=16, help='')

#training
model_config.add_argument('--lr', type=eval, default=0.0001, help='')
model_config.add_argument('--epochs', type=eval, default=500, help='')
model_config.add_argument('--batch_size', type=eval, default=128, help='')
model_config.add_argument('--dataset', type=str, default="None", help='')

#load trained weight
model_config.add_argument('--load_weights', type=str, default="None", help='')

#eye
model_config.add_argument('--eye', type=str, default="None", help='')

def get_config():
  config, unparsed = model_config.parse_known_args()
  print(config)
  return config, unparsed
