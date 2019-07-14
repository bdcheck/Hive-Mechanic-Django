import React, { Component } from 'react';

import '@material/react-top-app-bar/dist/top-app-bar.css';
import TopAppBar, {TopAppBarFixedAdjust} from '@material/react-top-app-bar';

import '@material/react-material-icon/dist/material-icon.css';
import MaterialIcon from '@material/react-material-icon';

import "@material/react-drawer/dist/drawer.css";
import Drawer, {
  DrawerHeader,
  DrawerSubtitle,
  DrawerTitle,
  DrawerContent,
  DrawerAppContent,
} from '@material/react-drawer';

import '@material/react-list/dist/list.css';
import List, {ListItem, ListItemGraphic, ListItemText} from '@material/react-list';

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

import detectBrowserLanguage from 'detect-browser-language'

import './App.css';

import translations from './data/Localizable.json';

import {Toolbox, DialogSequence, Game} from './Toolbox'

import demo from './data/Demo'

// eslint-disable-next-line
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

class App extends Component {
	state = {
		open: false
	};

    render() {
        return (
			<div className='drawer-container'>
				<TopAppBar
					title='SMS Dialog Builder'
					navigationIcon={<MaterialIcon
						icon='menu'
						onClick={() => this.setState({open: !this.state.open})}
					/>}
					actionItems={[<MaterialIcon key='item' icon='save' />]}
				/>

				<TopAppBarFixedAdjust className='top-app-bar-fix-adjust'>
					<Drawer
						dismissible
						open={this.state.open}>
						<DrawerHeader>
							<DrawerTitle tag='h3'>
								Sequences
							</DrawerTitle>
						</DrawerHeader>

						<DrawerContent>
							<List 
								singleSelection
								selectedIndex={this.state.selectedIndex}
								handleSelect={(selectedIndex) => this.setState({selectedIndex})}
							>
								{demo.map((sequence, index) => (
									<ListItem>
										<ListItemGraphic graphic={<MaterialIcon icon='call_split'/>} />
										<ListItemText primaryText={ sequence.name } />
									</ListItem>
								))}
							</List>
						</DrawerContent>
					</Drawer>
					<DrawerAppContent className='drawer-app-content'>
						<Game definition={demo} />
					</DrawerAppContent>
				</TopAppBarFixedAdjust>
			</div>
        );
    }
}

export default App;
