package telegram

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"path"
	"strconv"
)

const (
	getUpdatesMethod = "getUpdates"
	sendMessageMethod = "sendMessage"
)

type Client struct {
	host string
	basePath string
	client http.Client
}

func New(host string, token string) Client {
	return Client{
		host: host,
		basePath: newBasePath(token),
		client: http.Client{},
	}
}

func newBasePath(token string) string {
	return "bot" + token
}

func (c *Client) Updates(offset int, limit int) ([]Update, error) {
	query := url.Values{}
	query.Add("offset", strconv.Itoa(offset))
	query.Add("limit", strconv.Itoa(limit))

	body, err := c.doRequest(getUpdatesMethod, query)
	if err != nil {
		return nil, fmt.Errorf("request to update: %w", err)
	}
	var updates UpdatesResponse

	if err := json.Unmarshal(body, &updates); err != nil {
		return nil, fmt.Errorf("decode json: %w", err)
	}

	return updates.Result, nil
}

func (c *Client) SendMessage(chatID int, text string) error {
	query := url.Values{}
	query.Add("chat_id", strconv.Itoa(chatID))
	query.Add("text", text)

	_, err := c.doRequest(sendMessageMethod, query)
	if err != nil {
		return fmt.Errorf("send message: %w", err)
	}
	return nil
}

func (c *Client) doRequest(method string, query url.Values) ([]byte, error) {
	u := url.URL{
		Scheme: "https",
		Host: c.host,
		Path: path.Join(c.basePath, method),
	}

	request, err := http.NewRequest(http.MethodGet, u.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	request.URL.RawQuery = query.Encode()

	response, err := c.client.Do(request)
	if err != nil {
		return nil, fmt.Errorf("send query: %w", err)
	}

	defer response.Body.Close()
	body, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, fmt.Errorf("read response: %w", err)
	}

	return body, nil
}