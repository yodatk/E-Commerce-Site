import React, {Component} from "react";
import axios from "axios";
import PurchaseTable from "../PurchaseTable";

export class PersonalPurchaseHistory extends Component {
    state = {
        purchases: []
    }

    componentDidMount() {
        axios.get(
            "/fetch_personal_purchases/" + this.props.getUserId())
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

export default PersonalPurchaseHistory;