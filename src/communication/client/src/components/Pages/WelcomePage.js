import React, {Component} from "react";
import {MDBContainer, MDBRow} from "mdbreact";
import OnlyHeaderComponent from "../OnlyHeaderComponent";
import {Button} from "semantic-ui-react";
import axios from "axios";
import  { Redirect } from 'react-router-dom'

export class WelcomePage extends Component {


    // send () {
    //     console.log('send called')
    //     // this.props.history.push('/fetch_awaiting_approvals/dqwdqw')
    //     // axios.post(
    //     //     "/some_fun_stuff")
    //     // .then((res) => {
    //     // }).catch(error => {
    //     // });
    //     // return <Redirect push to={{pathname: '/fetch_awaiting_approvals/dqwdqw'}} />
    // }
    // render() {
    //     return (
    //         // <OnlyHeaderComponent header="Welcome"/>
    //         <Button onClick={this.send}>Some fun stuff</Button>
    //     );
    // }
    render() {
        return <OnlyHeaderComponent header={"Welcome"}/>
    }
}

export default WelcomePage;