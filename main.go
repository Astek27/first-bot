package main

import (
	"flag"
	"log"

	"github.com/Astek27/first-bot/clients/telegram"
)

const (
	tgBotHost = "api.telegram.org"
)

func main() {
	tgClient := telegram.New(tgBotHost, mustToken())
}

func mustToken() string {
	token := flag.String("bot-token", "", "bot token to access telegram")
	flag.Parse()

	if *token == "" {
		log.Fatal("bot-token is empty")
	}

	return *token
}