import React, { Component } from 'react';
import './Toolbox.css';

import '@material/react-card/dist/card.css';
import Card, {
  CardPrimaryContent,
  CardMedia,
  CardActions,
  CardActionButtons,
  CardActionIcons
} from "@material/react-card";


import '@material/react-typography/dist/typography.css';
import {
  Body1,
  Body2,
  Button,
  Caption,
  Headline1,
  Headline2,
  Headline3,
  Headline4,
  Headline5,
  Headline6,
  Overline,
  Subtitle1,
  Subtitle2,
} from '@material/react-typography';

import '@material/react-layout-grid/dist/layout-grid.css';
import {
  Grid,
  Row,
  Cell,
} from '@material/react-layout-grid';

import '@material/react-select/dist/select.css';
import Select from '@material/react-select';

import '@material/react-icon-button/dist/icon-button.css';
import IconButton from '@material/react-icon-button';
import MaterialIcon from '@material/react-material-icon';

import detectBrowserLanguage from 'detect-browser-language'
import translations from './data/Localizable.json';
import standardCards from './data/Cards.json';

import '@material/react-text-field/dist/text-field.css';
import TextField, { HelperText, Input } from '@material/react-text-field';

function translated(key) {
	var browserLanguage = detectBrowserLanguage();
    var languages = Object.keys(translations);
    
    for (var i = 0; i < languages.length; i++) {
    	var languageCode = languages[i];
    	
    	if (browserLanguage.startsWith(languageCode)) {
    		if (translations[languageCode][key] !== undefined) {
    			return translations[languageCode][key];
    		}
    	}
    }

    return key
}

var AvailableCards = {};

class DialogSequence extends Component {
    render() {
        return (
			<Row>
				<Cell columns={12}>
					<h5
						style={{
							marginBottom: "0px",
							marginTop: "0px",
							textAlign: "left"
						}}
					>{this.props.title ? this.props.title : "Title Me!"}</h5>
				</Cell>

				{this.props.items.map((item, index) => {
					if (AvailableCards[item["type"]] === undefined) {
						return React.createElement(Cell, {
							columns: 4
						}, React.createElement(AvailableCards["*"], {
							title: translated(item["name"]),
							updateCardOptions: this.props.updateCardOptions
						}, null));
					}
					
					item['updateCardOptions'] = this.props.updateCardOptions;
					
					return React.createElement(Cell, {
						columns: 6
					}, React.createElement(AvailableCards[item["type"]], item, null));
				})}
				<Cell columns={12}>
					<hr style={{
						marginBottom: "24px"
					}} />
				</Cell>
			</Row>
        );
    }
}

class DialogCard extends Component {
    constructor() {
        super()
    }
    
    loadOptions() {
    	this.props.updateCardOptions(this.props.title, this.props.configuration);
    }

    render() {
        return (<Card onClick={ this.loadOptions.bind(this)  }>
					<CardPrimaryContent>
						<Subtitle1 style={{
							textAlign: "left",
							marginTop: "1em",
							marginLeft: "1em",
							marginRight: "1em",
							marginBottom: 0,
						}}>
							{this.props.title ? this.props.title : "Need a card type"}: {this.props.name ? this.props.name : "Need a Name"}
						</Subtitle1>
						<Caption style={{
							marginTop: 0,
							padding: "1em",
							backgroundColor: "#B3E5FC",
							textAlign: "left"
						}}>
							{this.props.context ? this.props.context : "Need context."}
						</Caption>
						<Body2 style={{
							margin: "1em",
						}}>
						{this.props.description ? this.props.description : "Subclass Me!"} 
						</Body2>
					</CardPrimaryContent>
				</Card>);
    }
    
    configuration() {
    	return(
			<CardActions>
	    		<span>(Options here)</span>
			</CardActions>
    	);
    }
}

class SendMessageCard extends Component {
	state = {
		value: ''
	};
	
	constructor(props) {
		super(props);
		
		this.state.value = props.message;
	}
	
    render() {
        return (
            <DialogCard title={translated("SendMessage.Name")} 
            	name={this.props.name}
            	context={this.props.context}
            	function={<div style={{
            		textAlign: "left"
            	}}>{ this.state.value }</div>}
            	description={<div style={{
            		textAlign: "left"
            	}}>{ this.state.value }</div>}
            	themeColor={translated("SendMessage.Color")} 
            	configuration={this.configuration()}
            	updateCardOptions={ this.props.updateCardOptions } />
        );
    }
  
    configuration() {
    	return(
			<CardActions>
				<Grid style={{
					padding: "0px",
					marginLeft: "8px",
					marginRight: "8px",
					marginBottom: "8px",
					width: "100%"
				}}>
					<Row>
						<Cell columns={10}>
							<TextField
								label='Message'
								textarea
								onTrailingIconSelect={() => this.setState({value: ''})}
								trailingIcon={<MaterialIcon role="button" icon="cancel"/>}
								style={{
									width: "100%"
								}}>
								<Input
									value={this.state.value}
									onChange={(e) => this.setState({value: e.target.value})} />
							</TextField>
						</Cell>
						<Cell columns={2} align="middle">
							<center><button class="mdc-icon-button material-icons">navigate_next</button></center>
						</Cell>
					</Row>
				</Grid>
			</CardActions>
    	);
    }
}

class SendPictureCard extends Component {
	state = {
		image: ''
	};

	constructor(props) {
		super(props);

		this.state.image = props.image;
	}
	
    render() {
        return (
            <DialogCard title={translated("SendPictureCard.Name")} 
            	function={<div style={{
            		textAlign: "left"
            	}}>{ this.state.message }</div>}
            	description={<div style={{
            		textAlign: "left"
            	}}><img src={ this.state.image } /></div>}
            	themeColor={translated("SendPictureCard.Color")} 
            	configuration={this.configuration()}
            	updateCardOptions={ this.props.updateCardOptions } />
        );
    }
    
    configuration() {
    	return(
			<CardActions>
				<Grid style={{
					padding: "0px",
					marginLeft: "8px",
					marginRight: "8px",
					marginBottom: "8px",
					width: "100%"
				}}>
					<Row>
						<Cell columns={10}>
							<TextField
								outlined
								label='Picture URL'
								onTrailingIconSelect={() => this.setState({image: ''})}
								trailingIcon={<MaterialIcon role="button" icon="cancel"/>}
								style={{
									width: "100%",
								}}>
								<Input
									value={this.state.image}
									onChange={(e) => this.setState({image: e.target.value})} />
							</TextField>
						</Cell>
						<Cell columns={2} align="middle">
							<center><button class="mdc-icon-button material-icons">navigate_next</button></center>
						</Cell>
					</Row>
				</Grid>
			</CardActions>
    	);
    }
}

class ProcessResponseCard extends Component {
	constructor(props) {
		super(props);

		this.state = {
			message: '',
			patterns: [{
					"pattern": "^[Yy]",
					"action": "continue-intro"
				}, {
					"pattern": "^[Nn]",
					"action": "nonconsent-thanks"
				}, {
					"pattern": ".*",
					"action": "consent-unclear"
				}]
		};
	}
	
    render() {
        return (
            <DialogCard title={translated("ProcessResponse.Name")} 
            	description={<div style={{
            		textAlign: "left"
            	}}>TODO: ITERATE PATTERNS AND TIMEOUT</div>}
            	themeColor={translated("ProcessResponse.Color")} 
            	configuration={this.configuration()}
            	updateCardOptions={ this.props.updateCardOptions } />
        );
    }
    
    updatePatterns(index, pattern, action) {
    	console.log("UPDATE PATTERN: " + index + " -- " + pattern + " -- " + action);
    }
    
    configuration() {
    	return(
			<CardActions>
				<Grid style={{
					padding: "8px"
				}}>
					<Row>
						<Cell columns={12}>
							<Subtitle2
								style={{
									margin: "0px",
									padding: "0px",
									textAlign: "left"
								}}
							>Response Patterns</Subtitle2>
						</Cell>
					</Row>
					{this.state.patterns.map((item, index) => (
						<Row style={{
							marginTop: "8px"
						}}>
							<Cell columns={4}>
								<TextField
									outlined
									label='Pattern'
									onTrailingIconSelect={() => this.setState()}
									trailingIcon={<MaterialIcon role="button" icon="cancel"/>}>
									<Input
										value={item.pattern}
										onChange={(e) => this.updatePatterns(index, e.target.value, item.action)} />
								</TextField>						
							</Cell>
							<Cell columns={6}>
								<TextField
									outlined
									label='Action'
									onTrailingIconSelect={() => this.setState()}
									trailingIcon={<MaterialIcon role="button" icon="check"/>}>
									<Input
										value={item.action}
										onChange={(e) => this.updatePatterns(index, item.pattern, e.target.value)} />
								</TextField>						
							</Cell>
							<Cell columns={2} align="middle">
								<center><button class="mdc-icon-button material-icons">navigate_next</button></center>
							</Cell>
						</Row>
					))}
					<Row style={{
						marginTop: "8px",
						marginBottom: "16px"
					}}>
						<Cell columns={12}>(Add Pattern)</Cell>
					</Row>
					<Row style={{
						marginTop: "16px"
					}}>
						<Cell columns={12}>
							<Subtitle2
								style={{
									margin: "0px",
									padding: "0px",
									textAlign: "left"
								}}
							>Timeout</Subtitle2>
						</Cell>
					</Row>
					<Row>
						<Cell columns={6}>
							<TextField
								outlined
								label='Duration'
								onTrailingIconSelect={() => this.setState()}
								trailingIcon={<MaterialIcon role="button" icon="cancel"/>}>
								<Input
									value={this.state.timeoutQuantity}
									onChange={(e) => this.setState({timeoutQuantity: e.target.value})} />
							</TextField>						
						</Cell>
						<Cell columns={4}>
							<Select
								outlined
								label='Time Unit'
								onChange={(evt) => console.log(evt)}
							>
								<option />
								<option value='minutes'>Minutes</option>
								<option value='hours'>Hours</option>
								<option value='days'>Days</option>
							</Select>
						</Cell>
						<Cell columns={2} align="middle">
							<center><button class="mdc-icon-button material-icons">navigate_next</button></center>
						</Cell>
					</Row>
				</Grid>
			</CardActions>
    	);
    }
}


class ProcessCookieCard extends Component {
	constructor(props) {
		super(props);

		this.state = {
			cookie: '',
			patterns: [{
					"pattern": "+",
					"action": "exit-consent-timeout"
				}, {
					"pattern": "",
					"action": "request-consent-again"
				}]
		};
	}
	
    render() {
        return (
            <DialogCard title={translated("ProcessCookie.Name")} 
            	description={<div style={{
            		textAlign: "left"
            	}}>TODO: ITERATE PATTERNS AND TIMEOUT</div>}
            	themeColor={translated("ProcessCookie.Color")} 
            	configuration={this.configuration()}
            	updateCardOptions={ this.props.updateCardOptions } />
        );
    }
    
    updatePatterns(index, pattern, action) {
    	console.log("UPDATE COOKIE: " + index + " -- " + pattern + " -- " + action);
    }
    
    configuration() {
    	return(
			<CardActions>
				<Grid style={{
					padding: "8px"
				}}>
					<Row style={{
						marginBottom: "8px"
					}}>
						<Cell columns={12}>
							<TextField
								outlined
								style={{
									width: "100%"
								}}
								label='Cookie Name'
								onTrailingIconSelect={() => this.setState()}
								trailingIcon={<MaterialIcon role="button" icon="cancel"/>}>
								<Input
									value={this.state.cookie}
									onChange={(e) => this.setState({cookie: e.target.value})} />
							</TextField>						
						</Cell>
					</Row>
					<Row>
						<Cell columns={12}>
							<Subtitle2
								style={{
									margin: "0px",
									padding: "0px",
									textAlign: "left"
								}}
							>Patterns</Subtitle2>
						</Cell>
					</Row>
					{this.state.patterns.map((item, index) => (
						<Row style={{
							marginTop: "8px"
						}}>
							<Cell columns={4}>
								<TextField
									outlined
									label='Pattern'
									onTrailingIconSelect={() => this.setState()}
									trailingIcon={<MaterialIcon role="button" icon="cancel"/>}>
									<Input
										value={item.pattern}
										onChange={(e) => this.updatePatterns(index, e.target.value, item.action)} />
								</TextField>						
							</Cell>
							<Cell columns={6}>
								<TextField
									outlined
									label='Action'
									onTrailingIconSelect={() => this.setState()}
									trailingIcon={<MaterialIcon role="button" icon="check"/>}>
									<Input
										value={item.action}
										onChange={(e) => this.updatePatterns(index, item.pattern, e.target.value)} />
								</TextField>						
							</Cell>
							<Cell columns={2} align="middle">
								<center><button class="mdc-icon-button material-icons">navigate_next</button></center>
							</Cell>
						</Row>
					))}
					<Row style={{
						marginTop: "8px",
						marginBottom: "16px"
					}}>
						<Cell columns={12}>(Add Pattern)</Cell>
					</Row>
				</Grid>
			</CardActions>
    	);
    }
}

class SetCookieCard extends Component {
	state = {
		cookie: '',
		value: '',
	};
	
    render() {
        return (
            <DialogCard title={translated("SetCookie.Name")} 
            	description={translated("SetCookie.Description")} 
            	themeColor={translated("SetCookie.Color")} 
            	configuration={this.configuration()}
            	updateCardOptions={ this.props.updateCardOptions } />
        );
    }

    configuration() {
    	return(				
    		<Grid style={{
				padding: "8px"
			}}>
				<Row style={{
					marginBottom: "8px"
				}}>
					<Cell columns={10}
						style={{
							padding: "8px"
						}}>
						<TextField
							outlined
							style={{
								width: "100%",
								marginBottom: "8px"
							}}
							label='Cookie Name'
							onTrailingIconSelect={() => this.setState()}
							trailingIcon={<MaterialIcon role="button" icon="cancel"/>}>
							<Input
								value={this.state.cookie}
								onChange={(e) => this.setState({cookie: e.target.value})} />
						</TextField>						
						<TextField
							outlined
							style={{
								width: "100%"
							}}
							label='Cookie Value'
							onTrailingIconSelect={() => this.setState()}
							trailingIcon={<MaterialIcon role="button" icon="cancel"/>}>
							<Input
								value={this.state.value}
								onChange={(e) => this.setState({value: e.target.value})} />
						</TextField>						
					</Cell>
					<Cell columns={2} align="middle">
						<center><button class="mdc-icon-button material-icons">navigate_next</button></center>
					</Cell>
				</Row>
			</Grid>
		);
    }
}

class Toolbox extends Component {
    render() {
        return (
            <div className="mdc-layout-grid__cell--span-2" style={{
                backgroundColor: "#E0E0E0",
                height: "100vh",
                overflowY: "scroll",
                borderLeft: "4px solid #6100EE"
            }}>
                <div style={{
                    height: 64 + "px",
                    margin: 0
                }}></div>
                <div style={{
                    width: "100%",
                  padding: "0px",
                    overflowY: "scroll"
                }}>
					{standardCards.map((row, index) => (
			            <DialogCard title={translated(row["Name"])} description={translated(row["Description"])} themeColor={row["Color"]} />
					))}
                </div>
            </div>
        );
    }
    
    static populateAvailableCards(cardList) {
		cardList["send-message"] = SendMessageCard;
		cardList["set-cookie"] = SetCookieCard;
		cardList["process-response"] = ProcessResponseCard;
		cardList["process-cookie"] = ProcessCookieCard;
		cardList["process-cookie"] = ProcessCookieCard;
		cardList["send-picture"] = SendPictureCard		;

		// Include ways to customize...
		
		cardList["*"] = DialogCard;
    }
}

Toolbox.populateAvailableCards(AvailableCards);

class Game extends Component {
	state = {
		dialogSequence: null
	}

	constructor(props) {
		super(props)
	}
	
	updateCardOptions(title, content) {
		this.setState({
			optionsCard: content,
			optionsTitle: title
		});
	}

    render() {
        return (
			<Grid>
				<Row>
					<Cell columns={4} style={{
						height: "100vh",
						overflowY: "scroll"
					}}>
						{ this.state.dialogSequence.selectedCard.sources }
					</Cell>
					<Cell columns={4} style={{
						height: "100vh",
						overflowY: "scroll"
					}}>
						{ this.state.dialogSequence.selectedCard }
						{ this.state.dialogSequence.selectedCard.configuration }
					</Cell>
					<Cell columns={4} style={{
						height: "100vh",
						overflowY: "scroll"
					}}>
						{ this.state.dialogSequence.selectedCard.destinaions }
					</Cell>
				</Row>
			</Grid>
        );
    }
}

export { Toolbox, DialogSequence, Game };
