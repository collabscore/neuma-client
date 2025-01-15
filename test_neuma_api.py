
import sys, os
import argparse
import json
from pathlib import Path
import requests

import environ

from requests.auth import HTTPBasicAuth

from neuma_client.client import NeumaClient

from neuma_client.proxies import Collections, Corpus, Opus, Source, Manifest, Edition

def main(argv=None):
	"""
	 Test of Neuma API client
	"""

	# On accepte des arguments
	parser = argparse.ArgumentParser(description='Neuma API tests')
	parser.add_argument('-b', '--base_url', dest='base_url',
                   help='URL of Neuma services', default="http://neuma.huma-num.fr")
	args = parser.parse_args()
	
	# On prend le compte et le mot de passe REST Neuma dans des variables d'environnement
	env = environ.Env(	# set casting, default value
    	NEUMA_REST_USER=(str, "annymous"),
    	NEUMA_REST_PASSWORD=(str, ""),
		)
	
	print (f"Base URL for Neuma services : {args.base_url}")

	print (f"User: {env('NEUMA_REST_USER')}")
	
	client = NeumaClient (None, auth_scheme="Token", base_url=args.base_url)
	#resp_login = client.login(env('NEUMA_REST_USER'), env('NEUMA_REST_PASSWORD'))

	# Test the welcome message
	res = client.request ("NeumaApi_v3")
	#print (f"Welcome service -- {res['message']}")
		
	res = client.request ("Element", full_neuma_ref= "all:collabscore:saintsaens-ref")
	#print (f"Recherche d'un corpus -- {res['title']}\n")

	res = client.request ("Element", full_neuma_ref= "all:collabscore:saintsaens-ref:C006_0")
	#print (f"Recherche d'un opus -- {res['title']}")

	opus = Opus (client, res)
	iiif = opus.get_source(Source.IIIF_REF)
	print (f"Recherche d'une source -- {iiif.ref}, {iiif.url}")

	editions = iiif.get_editions()
	for ed in editions:
		print (f"\tEditions sur la source -- {iiif.ref}:  {ed.name}")
		if ed.name == "describe_part":
			print (f"\t\tValeur du parametre 'part' :  {ed.get_param('part')}")
			
	#resp = iiif.post_editions([{"name": "describe_part", "params": {}}])
	#print (f"\t\tResult of post edition: {resp}")
	iiif_manifest = iiif.get_iiif_manifest()

	"""
	    Test with proxies
	"""
	corpus_ref = "all:collabscore:saintsaens-ref"
	print ("\n\n")
	print ("\t\t Test of proxies\n")
	neuma_coll = Collections (client)
	corpus = neuma_coll.get_corpus (corpus_ref)
	print (f"Got corpus {corpus.ref}")
	opuses = corpus.get_opus_list()
	for op in opuses:
		print (f"\tOpus {op.ref} with title {op.title}")
		iiif = op.get_source(Source.IIIF_REF)
		if iiif is None:
			print (f"Unable to find source IIIF for opus {op.ref}")
		elif iiif.has_manifest:
			manifest = iiif.get_manifest()
			print (f"\t\tSource IIIF : {iiif.ref}. Nb pages: {manifest.nb_pages()}")
			for i in range (manifest.nb_pages()):
				page = manifest.get_page(i)
				print (f"\t\t\tPage {i+1}. URL: {page['url']} ({page['width']}) Nb systems: {manifest.nb_systems(i)}")
				for j in range (manifest.nb_systems(i)):
					system = manifest.get_system(i,j)
					print (f"\t\t\t\tSystem {j+1} : Nb staves: {manifest.nb_staves(i,j)}")
					print (f"\t\t\t\tSystem {j+1} : Region: {manifest.system_region(i,j)}")
					print (f"\t\t\t\tSystem {j+1} : Nb measures: {manifest.nb_measures(i,j)}")						

	
if __name__ == "__main__":
	main()