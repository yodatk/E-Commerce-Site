import React, {Component} from "react";
import axios from "axios";
import PurchaseTable from "../PurchaseTable";
import {withRouter} from "react-router-dom";

export class StorePurchaseHistory extends Component {
    state = {
        purchases: []
    }

    componentDidMount() {
        axios.get(
            `/fetch_store_purchases/${this.props.getUserId()}/${this.props.match.params.storename}`)
            .then((res) => {
                this.setState({purchases: res.data !== null && 'purchases' in res.data ? res.data.purchases : []})
                console.log(res.data.purchases)
            }).catch(error => {
            console.log(error)
        });
    }

    render() {
        return (
            <PurchaseTable purchases={this.state.purchases}/>
        );
    }
}

export default withRouter(StorePurchaseHistory);